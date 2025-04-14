Security Considerations
=======================

Secret Management
-----------------

sfs-settings uses the `keyring` library to securely store and retrieve secrets. This provides several advantages:

1. Secrets are not stored in plain text
2. System-specific secure storage is used (Keychain on macOS, Secret Service on Linux, Credential Manager on Windows)
3. Secrets are isolated from code and configuration files

Best Practices
--------------

1. **Use reobtain_each_usage=True for secrets**
   This ensures you always get the latest value, important if secrets are rotated.

2. **Use validation functions**
   Validate that secrets match expected formats to catch misconfiguration early.

3. **Seperate your public settings in .env files from secret settings in your secrets manager**
   With this module, it is actually easy and practical to have a .env file for public settings because secrets can be dynamically retrieved from the secrets manager.  This makes operation in even local and cloud environments safer and easier since secrets have minimal exposure even during operation.

4. **Use different store_names for different applications**
   This prevents one application from accessing another's secrets.

Lifetime considerations
-----------------------

When obtaining the actual secret value, the final value you get is stored where ever you immediately assign it.  You are responsible for deleting the value from memory when you are done with it.  No matter how this module can try, it cannot delete the value from memory for you.  It can only handle what it does safely.

.. warning::
    The current implementation uses strings to store the secret value.  This functionally causes the secret to exist in memory for an indefinite period of time.  There are no mitigations when using strings.  This is a known issue and will be fixed by using bytes which can be deleted from memory.

.. code-block:: python

    set_secret_var_locally(
        "API_KEY",
        "MyApp",
        "api_secret",
    )

    def print_api_key():
        global API_KEY
        local_copy = API_KEY
        print(local_copy)

        # doesn't entirely delete the value from memory, but it does help because it allows the possibility of it being garbage collected.
        del local_copy

Validator Functions
-------------------

Always add validator functions to ensure secrets have the expected format:

.. code-block:: python

    def api_key_validator(value):
        # Check that the API key is at least 16 characters and starts with "key_"
        return isinstance(value, str) and len(value) >= 16 and value.startswith("key_")

    set_secret_var_locally(
        "API_KEY",
        "MyApp",
        "api_secret",
        validator_function=api_key_validator
    )

    def print_api_key():
        global API_KEY
        print(API_KEY)

Handling Default Values
-----------------------

Be careful with default values for secrets. In most cases, it's better to fail loudly if a secret is missing rather than using a default:

.. code-block:: python

    # Good: Will raise an error if API_KEY is not set
    set_secret_var_locally("API_KEY", "MyApp", "api_secret")

    # Risky: Provides a default that might be used in production by mistake
    set_secret_var_locally("API_KEY", "MyApp", "api_secret", default="test_key_12345")
