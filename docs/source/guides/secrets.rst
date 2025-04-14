Working with Secrets
====================

This guide explains how to work with secrets in sfs-settings.

Basic Usage
-----------

.. code-block:: python

    from sfs_settings import set_secret_var_locally

    set_secret_var_locally("API_KEY", "MyApp", "api_key")

    # Now API_KEY is available in your module
    print(API_KEY)
