Using python-settings with Libraries
====================================

This example shows how to use python-settings when creating a reusable Python library.

Library Design Considerations
-----------------------------

When creating libraries that need configuration, you should:

1. Avoid polluting the global namespace
2. Make configuration explicit and discoverable
3. Provide reasonable defaults
4. Allow users to customize settings

Pattern Recommendation
----------------------

For libraries, the **return pattern** is recommended as it's the most explicit and doesn't
modify the module namespace:

.. code-block:: python

    # my_library/config.py
    from python_settings import return_env_var, return_secret_var

    # Configuration with defaults suitable for library use
    API_TIMEOUT = return_env_var("MY_LIB_API_TIMEOUT", default="30", conversion_function=int)
    MAX_RETRIES = return_env_var("MY_LIB_MAX_RETRIES", default="3", conversion_function=int)
    API_KEY = return_secret_var("API_KEY", "MyLibrary", "api_key", default=None)

Complete Example
----------------

Here's a complete example of a library that uses python-settings:

Project Structure
~~~~~~~~~~~~~~~~~

.. code-block:: text

    my_library/
    ├── __init__.py
    ├── config.py
    └── client.py

Configuration Module
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
    :caption: my_library/config.py

    from python_settings import return_env_var, return_secret_var

    # Public configuration with reasonable defaults
    DEBUG = return_env_var("MY_LIB_DEBUG", default="false",
                          conversion_function=lambda x: x.lower() == "true")
    TIMEOUT = return_env_var("MY_LIB_TIMEOUT", default="30",
                            conversion_function=int)
    MAX_RETRIES = return_env_var("MY_LIB_MAX_RETRIES", default="3",
                                conversion_function=int)

    # Optional API key - allowing the library to work without authentication
    # for public APIs or with authentication for private APIs
    API_KEY = return_secret_var(
        "MyLibrary",
        "api_key",
        default=None,
        reobtain_each_usage=True
    )

Client Module
~~~~~~~~~~~~~

.. code-block:: python
    :caption: my_library/client.py

    import requests
    from . import config

    class ApiClient:
        def __init__(self, custom_api_key=None, custom_timeout=None):
            # Allow runtime overrides of configuration
            self.api_key = custom_api_key or config.API_KEY
            self.timeout = custom_timeout or config.TIMEOUT
            self.max_retries = config.MAX_RETRIES
            self.debug = config.DEBUG

        def get_data(self, endpoint):
            """Make an API request with configured settings"""
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            if self.debug:
                print(f"Making request to {endpoint} with timeout={self.timeout}")

            for attempt in range(self.max_retries):
                try:
                    response = requests.get(
                        endpoint,
                        headers=headers,
                        timeout=self.timeout
                    )
                    response.raise_for_status()
                    return response.json()
                except Exception as e:
                    if self.debug:
                        print(f"Attempt {attempt+1} failed: {e}")
                    if attempt == self.max_retries - 1:
                        raise

            return None  # Should never reach here

Usage Example
~~~~~~~~~~~~~

.. code-block:: python
    :caption: Using the library

    from my_library.client import ApiClient

    # Uses environment variables and/or secrets for configuration
    client = ApiClient()
    data = client.get_data("https://api.example.com/data")

    # Or with custom settings
    custom_client = ApiClient(
        custom_api_key="my-custom-key",
        custom_timeout=60
    )
    data = custom_client.get_data("https://api.example.com/data")

Best Practices for Libraries
----------------------------

1. **Use prefixes for environment variables**

   Prefix your environment variables with your library name to avoid conflicts:

   .. code-block:: python

       DATABASE_URL = return_env_var("MYLIB_DATABASE_URL", default=None)

2. **Provide reasonable defaults**

   Make your library work out-of-the-box with sensible defaults:

   .. code-block:: python

       TIMEOUT = return_env_var("MYLIB_TIMEOUT", default="30", conversion_function=int)

3. **Allow runtime overrides**

   Let users override settings at runtime through your API:

   .. code-block:: python

       def __init__(self, timeout=None):
           self.timeout = timeout or config.TIMEOUT

4. **Document all configuration options**

   Make sure to document all environment variables and secrets your library uses.
