Advanced Usage
==============

This guide covers advanced techniques for using python-settings in complex scenarios.

Type Conversion and Validation
------------------------------

Custom Type Conversion
~~~~~~~~~~~~~~~~~~~~~~

For complex types, you can provide custom conversion functions:

.. code-block:: python

    import json
    from datetime import datetime

    # Convert JSON string to dict
    set_env_var_locally(
        "CONFIG_JSON",
        conversion_function=json.loads
    )

    # Convert ISO date string to datetime
    def parse_date(date_str):
        return datetime.fromisoformat(date_str)

    set_env_var_locally(
        "EXPIRY_DATE",
        conversion_function=parse_date
    )

Advanced Validation
~~~~~~~~~~~~~~~~~~~

Implement complex validation logic:

.. code-block:: python

    def validate_url(url):
        """Ensure URL uses HTTPS and has valid format"""
        return (
            url.startswith("https://") and
            len(url) > 10 and
            "." in url.split("//")[1]
        )

    set_env_var_locally(
        "API_BASE_URL",
        validator_function=validate_url
    )

    # Validate numeric ranges
    def validate_port(port):
        return 1024 <= port <= 65535

    set_env_var_locally(
        "PORT",
        conversion_function=int,
        validator_function=validate_port
    )

Dynamic Configuration
---------------------

Reobtaining Values Dynamically
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use `reobtain_each_usage=True` to get fresh values on each access:

.. code-block:: python

    # Useful for values that might change during runtime
    set_env_var_locally(
        "DYNAMIC_CONFIG",
        reobtain_each_usage=True
    )

    # Example usage:
    def long_running_process():
        while True:
            # Will check environment variable on each loop iteration
            if DYNAMIC_CONFIG == "stop":
                break
            process_data()
            time.sleep(1)

Combining Multiple Patterns
---------------------------

Mixing Approaches for Complex Apps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For larger applications, you might use multiple patterns:

.. code-block:: python

    # config.py
    from python_settings import (
        set_env_var_locally,
        return_env_var,
        return_secret_var
    )

    # Basic config with local pattern
    set_env_var_locally("DEBUG")
    set_env_var_locally("LOG_LEVEL")

    # More complex settings with return pattern
    database_config = {
        "host": return_env_var("DB_HOST", default="localhost"),
        "port": return_env_var("DB_PORT", default="5432", conversion_function=int),
        "name": return_env_var("DB_NAME", default="app"),
        "user": return_env_var("DB_USER", default="postgres"),
        "password": return_secret_var("AppDB", "db_password"),
    }

    # Create a connection string from components
    def build_connection_string():
        return (f"postgresql://{database_config['user']}:{database_config['password']}"
                f"@{database_config['host']}:{database_config['port']}"
                f"/{database_config['name']}")

    DATABASE_URL = build_connection_string()

Working with Pydantic
~~~~~~~~~~~~~~~~~~~~~

Integrate python-settings with Pydantic models:

.. code-block:: python

    from pydantic import BaseModel, Field
    from python_settings import return_env_var, return_secret_var

    class DatabaseSettings(BaseModel):
        host: str = Field(default_factory=lambda: return_env_var("DB_HOST", default="localhost"))
        port: int = Field(default_factory=lambda: return_env_var("DB_PORT", default="5432", conversion_function=int))
        username: str = Field(default_factory=lambda: return_env_var("DB_USER", default="postgres"))
        password: str = Field(default_factory=lambda: return_secret_var("AppDB", "db_password"))
        database: str = Field(default_factory=lambda: return_env_var("DB_NAME", default="app"))

        @property
        def url(self) -> str:
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

    class Settings(BaseModel):
        debug: bool = Field(default_factory=lambda: return_env_var("DEBUG", default="false", conversion_function=lambda x: x.lower() == "true"))
        log_level: str = Field(default_factory=lambda: return_env_var("LOG_LEVEL", default="info"))
        database: DatabaseSettings = Field(default_factory=DatabaseSettings)

    # Usage
    settings = Settings()
    print(f"Database URL: {settings.database.url}")
    print(f"Debug mode: {settings.debug}")

Error Handling
--------------

Graceful Error Handling
~~~~~~~~~~~~~~~~~~~~~~~

Custom error handling for configuration issues:

.. code-block:: python

    from python_settings import SettingsValidationError, SettingsNotFoundError
    import sys

    try:
        set_env_var_locally(
            "API_KEY",
            validator_function=lambda x: len(x) >= 32 and x.startswith("key_")
        )
    except SettingsValidationError:
        print("ERROR: API_KEY must be at least 32 characters and start with 'key_'")
        print("Please set a valid API_KEY in your environment or .env file")
        sys.exit(1)
    except SettingsNotFoundError:
        print("ERROR: API_KEY is required but not set")
        print("Please set API_KEY in your environment or .env file")
        sys.exit(1)

Fallback Mechanisms
~~~~~~~~~~~~~~~~~~~

Implement multiple levels of fallbacks:

.. code-block:: python

    def get_configuration():
        # Try environment variables first
        try:
            return return_env_var("CONFIG_PATH")
        except SettingsNotFoundError:
            pass

        # Try standard locations
        standard_paths = [
            "./config.json",
            "~/.config/myapp/config.json",
            "/etc/myapp/config.json"
        ]

        for path in standard_paths:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                return expanded_path

        # Fall back to defaults
        return None

Performance Considerations
--------------------------

For performance-critical applications, consider:

1. **Minimize dynamic reloading**: Use `reobtain_each_usage=False` (the default) when possible
2. **Cache converted values**: Avoid repeated parsing of complex values
3. **Load settings at startup**: Initialize all settings at application startup rather than on-demand

.. code-block:: python

    # Example of efficient settings initialization
    def initialize_settings():
        """Initialize all application settings at startup"""
        try:
            set_env_var_locally("DEBUG", conversion_function=lambda x: x.lower() == "true")
            set_env_var_locally("PORT", conversion_function=int)
            set_env_var_locally("API_URL")
            # ... more settings
            return True
        except (SettingsValidationError, SettingsNotFoundError) as e:
            print(f"Failed to initialize settings: {e}")
            return False

    # In application startup:
    if not initialize_settings():
        sys.exit(1)
