.. _cloud_deployment:

Cloud Deployment
================

Backend Configuration
---------------------

sfs-settings provides a more flexible approach to keyring backend configuration:

.. code-block:: python
    :caption: app_config.py

    import re
    import keyring
    from keyring_aws import AWSKeyring
    from keyring_gcp import GCPKeyring

    # Register different backends for different secret services
    keyring.register_backend_for_service(
        "AWS-*",  # Any service starting with AWS-
        lambda: AWSKeyring()
    )

    keyring.register_backend_for_service(
        re.compile(r"GCP-.*"),  # Regex pattern for GCP services
        lambda: GCPKeyring()
    )

    # Use the default system keyring for anything else
    keyring.register_default_backend(lambda: keyring.backends.SecretService.Keyring())

    # Now in your code, secrets will automatically use the right backend
    from sfs_settings import set_secret_var_locally

    # Uses AWS backend
    set_secret_var_locally("AWS_SECRET", "AWS-MyApp", "aws_secret")

    # Uses GCP backend
    set_secret_var_locally("GCP_SECRET", "GCP-MyApp", "gcp_secret")

    # Uses default backend
    set_secret_var_locally("LOCAL_SECRET", "MyApp", "local_secret")
