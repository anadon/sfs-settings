sfs-settings quickstart
=======================

This example shows how to use sfs-settings in a command-line interface (CLI) tool.

CLI Tool Considerations
-----------------------

CLI tools have specific needs:

1. Settings from environment variables, config files, and command-line arguments
2. Secret handling for API keys and credentials
3. Different modes for interactive vs automated use

Installation
------------

Requirements
~~~~~~~~~~~~

* Python 3.11+
* Poetry 1.9+
* Pydantic 2.0+
* keyring 25.0.0+
* python-dotenv 0.9.0+

Basic Installation
~~~~~~~~~~~~~~~~~~

Using pip
_________

.. code-block:: bash

    pip install sfs-settings

Using Poetry
____________

.. code-block:: bash

    poetry add sfs-settings

From Source
___________

.. code-block:: bash

    git clone https://github.com/anadon/sfs-settings.git
    cd sfs-settings
    poetry install

Pattern Recommendation
----------------------

Here are examples of all three patterns.

#. Set values in the **containing module** namespace.
#. Set values in the **sfs module** so users don't have to create their own settings module.
#. **Explicitly returns** values for manual assignment and does not have any side effects (unless a passed, non-default function causes side effects).

.. note::
    While error catching is shown below, it is advised to not use it unless you have a specific reason.  Any errors that occur will generally be raised at startup and are easier to debug if they are left alone.

.. code-block:: python
    :caption: $PROJECT_ROOT/config.py, all possible imports

    from sfs_settings import (
        SettingsNotFoundError,
        SettingsValidationError,
        return_env_var,
        return_secret_var,
        set_env_var_locally,
        set_secret_var_locally,
        track_env_var,
        track_secret_var,
    )

.. code-block:: python
    :caption: $PROJECT_ROOT/config.py, set values in the module namespace

    # Settings are available directly in the module namespace
    set_env_var_locally("ENV_1", default="unset")
    set_secret_var_locally("API_TOKEN", "MyCLI", "api_token", default="unset")

.. code-block:: python
    :caption: $PROJECT_ROOT/config.py, set values in the sfs_settings namespace with error handling

    # Settings are available directly in the sfs_settings namespace
    try:
        track_env_var("ENV_2", default="unset")
    except SettingsNotFoundError as e:
        print("Could not set ENV_2 as ENV_2 isn't an environment variable.")
    try:
        track_secret_var("PASSWORD", "MyCLI", "password", reobtain_each_usage=False)
    except SettingsNotFoundError as e:
        print("Could not set PASSWORD as it does not exist.")

.. code-block:: python
    :caption: $PROJECT_ROOT/config.py, explicitly return values for manual assignment

    # Settings are explicitly returned
    try:
        from validators import url
        ENV_3 = return_env_var("ENV_3", validator_function=url, default="https://example.com")
    except SettingsValidationError as e:
        print("Could not set ENV_3 as ENV_3 does not pass validation.")
    try:
        from base64 import b64decode
        PRIVATE_KEY = return_secret_var("gpg", "private_key", conversion_function=b64decode)
    except Exception as e:
        print("left to the implementor of the conversion function.")


.. code-block:: python
    :caption: $PROJECT_ROOT/config.py, using the settings

    # Now use these variables directly
    print(f"ENV_1: {ENV_1}")
    print(f"API_TOKEN: {API_TOKEN}")
    print(f"ENV_2: {sfs.ENV_2}")
    print(f"PASSWORD: {sfs.PASSWORD}")
    print(f"ENV_3: {ENV_3}")
    print(f"PRIVATE_KEY: {PRIVATE_KEY}")

.. code-block:: python
    :caption: $PROJECT_ROOT/__main__.py, using the settings

    import config
    import sfs_settings as sfs

    print(f"ENV_1: {config.ENV_1}")
    print(f"API_TOKEN: {config.API_TOKEN}")
    print(f"ENV_2: {sfs.ENV_2}")
    print(f"PASSWORD: {sfs.PASSWORD}")
    print(f"ENV_3: {config.ENV_3}")
    print(f"PRIVATE_KEY: {config.PRIVATE_KEY}")
