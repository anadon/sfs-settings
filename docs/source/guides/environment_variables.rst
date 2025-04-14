Working with Environment Variables
==================================

This guide explains how to work with environment variables in python-settings.

Basic Usage
-----------

Environment variables are a common way to configure applications. Python-settings makes them easy to use:

.. code-block:: python

    from python_settings import set_env_var_locally

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

Python-settings automatically loads variables from .env files in the current directory:

.. code-block:: bash
    :caption: .env file

    DATABASE_URL=postgres://user:pass@localhost/db
    DEBUG=true
    PORT=5000

Different environments can have different .env files:

.. code-block:: bash
    :caption: .env.development

    DATABASE_URL=postgres://user:pass@localhost/dev_db
    DEBUG=true

.. code-block:: bash
    :caption: .env.production

    DATABASE_URL=postgres://user:pass@prod-server/prod_db
    DEBUG=false

Loading specific environments:

.. code-block:: python
    :caption: Loading specific environments

    import os
    from dotenv import load_dotenv

    # Before importing python_settings
    load_dotenv(f".env.{os.environ.get('ENVIRONMENT', 'development')}")

    from python_settings import set_env_var_locally
