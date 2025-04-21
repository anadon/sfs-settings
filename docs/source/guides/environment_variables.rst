Working with Environment Variables
==================================

This guide explains how to work with environment variables in sfs-settings.

Basic Usage
-----------

Environment variables are a common way to configure applications. sfs-settings makes them easy to use:

.. code-block:: python

    from sfs_settings import set_env_var_locally

    # Set DATABASE_URL from environment variable
    set_env_var_locally("DATABASE_URL")

    # Now you can use DATABASE_URL directly
    print(f"Connecting to {DATABASE_URL}")

Type Conversion
---------------

Environment variables are always strings, but you can convert them to the right type:

.. code-block:: python

    # Convert PORT to an integer
    set_env_var_locally("PORT", conversion_function=int)

    # Convert DEBUG to a boolean
    def to_bool(value):
        return value.lower()[0] in ("y", "t", "1")

    set_env_var_locally("DEBUG", conversion_function=to_bool)

Working with .env Files
-----------------------

sfs-settings automatically loads variables from .env files in the current directory:

.. code-block:: bash
    :caption: .env file

    DATABASE_URL=postgres://user:pass@localhost/db
    DEBUG=true
    PORT=5000
