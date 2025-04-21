# ruff: noqa: D400,D415,D417
"""
SFS Settings: Simple, Flexible, and Secure Settings Management
==============================================================

This module provides a flexible, secure way to manage application settings from
environment variables and secret stores. It offers three distinct patterns:

1. Setting variables directly in the sfs_settings module
2. Setting variables in the calling module namespace
3. Returning values for manual assignment

Key Features:
-------------
* Environment variable integration with .env file support
* Secure secret storage via the keyring library
* Type conversion and validation
* Lazy evaluation with reobtain_each_usage option
* Stack inspection to modify the correct module namespace

Basic Examples:
---------------
Set and get in sfs-settings itself:

.. code-block:: python

    import sfs_settings as sfs
    sfs.track_env_var("DATABASE_URL")
    print(sfs.DATABASE_URL)  # Uses the value from DATABASE_URL environment variable

Set and get in the calling module:

.. code-block:: python

    from sfs_settings import set_env_var_locally
    set_env_var_locally("DATABASE_URL")
    print(DATABASE_URL)  # Variable is now available in the local namespace

Use values directly:

.. code-block:: python

    from sfs_settings import return_env_var
    db_url = return_env_var("DATABASE_URL")
    print(db_url)
"""

from __future__ import annotations

from dotenv import load_dotenv

from .core_functions import (
    return_env_var,
    return_secret_var,
    set_env_var_locally,
    set_secret_var_locally,
    track_env_var,
    track_secret_var,
)
from .exceptions import SettingsNotFoundError, SettingsValidationError

__all__ = [
    "SettingsNotFoundError",
    "SettingsValidationError",
    "return_env_var",
    "return_secret_var",
    "set_env_var_locally",
    "set_secret_var_locally",
    "track_env_var",
    "track_secret_var",
]

__version__ = "0.9.4"

# This loads values from a .env file into the os.environ
load_dotenv()

DEBUG_sfs_settings = False
