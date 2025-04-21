FastAPI Example
===============

FastAPI projects often require alternative configurations for a number of different environments.  Here is
outlined how sfs-settings provides a more consistent pattern for setting the application's various
configurations.  The example shown scales to setting values in multiple files as well as providing more
advanced features such as reloading on each access.

Project Structure
-----------------

.. code-block:: text

    myapp/
    ├── .env
    ├── app.py
    └── config.py

Configuration Module
--------------------

.. code-block:: python
    :caption: config.py

    from sfs_settings import track_env_var, track_secret_var

    # Environment variables
    track_env_var("APP_NAME")
    track_env_var("ADMIN_EMAIL")
    track_env_var("ITEMS_PER_USER", conversion_function=int, reload_on_access=True)

    # Secrets
    track_secret_var("SECRET_KEY", "MyApp", "myapp_secret")
    track_secret_var("API_KEY", "MyApp", "myapp_external_api_key")

Application Code
----------------

.. code-block:: python
   :caption: mod_name/app.py

   from fastapi import FastAPI

   import sfs_settings as sfs

   app = FastAPI()

   @app.get("/info")
   async def info():
       return {
           "app_name": sfs.APP_NAME,
           "admin_email": sfs.ADMIN_EMAIL,
           "items_per_user": sfs.ITEMS_PER_USER,
       }

Environment File
----------------

.. code-block:: text
    :caption: .env

    FLASK_ENV=development
    DATABASE_URL=sqlite:///dev.db
    DEBUG=true
