Flask Example
=============

This example shows how to use sfs-settings in a Flask web application.

Project Structure
-----------------

.. code-block:: text

    myapp/
    ├── .env
    ├── app.py
    ├── config.py
    └── requirements.txt

Configuration Module
--------------------

.. code-block:: python
    :caption: config.py

    from sfs_settings import set_env_var_locally, set_secret_var_locally

    # Environment variables
    set_env_var_locally("FLASK_ENV", default="development")
    set_env_var_locally("DATABASE_URL")
    set_env_var_locally("DEBUG", conversion_function=lambda x: x.lower() == "true")
    set_env_var_locally("PORT", conversion_function=int, default="5000")

    # Secrets
    set_secret_var_locally("SECRET_KEY", "MyApp", "flask_secret")
    set_secret_var_locally("API_KEY", "MyApp", "external_api_key")

Application Code
----------------

.. code-block:: python
    :caption: mod_name/app.py

    import config  # This sets up all our environment variables and secrets
    from flask import Flask

    app = Flask(__name__)

    # Now we can use the variables directly
    SECRET_KEY = app.config["SECRET_KEY"] # Note: what is stored is a snapshot of the secret.  If it changes in the secrets manager, it will not be reflected here.
    DEBUG = app.config["DEBUG"]

    @app.route('/')
    def home():
        return f"Running in {FLASK_ENV} mode"

    if __name__ == "__main__":
        app.run(port=PORT)

Environment File
----------------

.. code-block:: text
    :caption: .env

    FLASK_ENV=development
    DATABASE_URL=sqlite:///dev.db
    DEBUG=true
