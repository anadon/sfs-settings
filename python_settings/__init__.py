# ruff: noqa: D400,D415,D417
"""
Python Settings: Simplified Environment and Secret Management
=============================================================

This module provides a flexible, secure way to manage application settings from
environment variables and secret stores. It offers three distinct patterns:

1. Setting variables directly in the python_settings module
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
Set and get in python-settings itself:

.. code-block:: python

    import python_settings as ps
    ps.track_env_var("DATABASE_URL")
    print(ps.DATABASE_URL)  # Uses the value from DATABASE_URL environment variable

Set and get in the calling module:

.. code-block:: python

    from python_settings import set_env_var_locally
    set_env_var_locally("DATABASE_URL")
    print(DATABASE_URL)  # Variable is now available in the local namespace

Use values directly:

.. code-block:: python

    from python_settings import return_env_var
    db_url = return_env_var("DATABASE_URL")
    print(db_url)
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from os import environ
from types import FrameType
from typing import Any

import keyring
from dotenv import load_dotenv
from pydantic import validate_call

from .python_settings_exceptions import SettingsNotFoundError, SettingsValidationError

# This loads values from a .env file into the os.environ
load_dotenv()

DEBUG_PYTHON_SETTINGS = False

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


@validate_call
def __obtain_convert_and_validate__(
    *,
    obtaining_function: Callable[[], str],
    conversion_function: Callable[[str], Any] | type,
    is_valid_function: Callable[[Any], bool] = lambda _: True,
) -> Any:
    value = obtaining_function()
    converted_value = conversion_function(value) if value is not None else None
    if not is_valid_function(converted_value):
        raise SettingsValidationError
    return converted_value


class __PseudoVariable__:  # noqa: N801
    __slots__ = ("conversion_function", "obtaining_function", "validator_function")

    @validate_call
    def __init__(
        self,
        obtaining_function: Callable[[], str],
        conversion_function: Callable[[str], Any] | type,
        validator_function: Callable[[Any], bool],
    ) -> None:
        self.obtaining_function = obtaining_function
        self.conversion_function = conversion_function
        self.validator_function = validator_function

    def _get_value(self) -> Any:
        """Get the actual value."""
        return __obtain_convert_and_validate__(
            obtaining_function=self.obtaining_function,
            conversion_function=self.conversion_function,
            is_valid_function=self.validator_function,
        )

    # Make it work for equality checks (api_key == "secret_value")
    def __eq__(self, other: object) -> bool:
        return self._get_value() == other

    # Make it work in string contexts (str(api_key) or print(api_key))
    def __str__(self) -> str:
        return str(self._get_value())

    def __repr__(self) -> str:
        return repr(self._get_value())

    # You can also make it callable if wanted (api_key())
    def __call__(self) -> Any:
        return self._get_value()


def __get_calling_module__() -> FrameType:
    for frame in inspect.stack():
        if (
            not (set(frame.filename.split("/")) | {"python_settings", "pydantic"})
            or "/python-settings/tests/" in frame.filename
        ):
            return frame.frame
    raise ValueError("Could not find calling module")  # pragma: no cover


def __get_this_module__() -> FrameType:
    return inspect.stack()[0].frame


@validate_call
def __returnable_value__(
    *,
    obtaining_function: Callable[[], str],
    conversion_function: Callable[[str], Any] | type,
    validator_function: Callable[[Any], bool],
    reobtain_each_usage: bool,
) -> Any:
    return (
        __PseudoVariable__(
            obtaining_function=obtaining_function,
            conversion_function=conversion_function,
            validator_function=validator_function,
        )
        if reobtain_each_usage
        else __obtain_convert_and_validate__(
            obtaining_function=obtaining_function,
            conversion_function=conversion_function,
            is_valid_function=validator_function,
        )
    )


def __set_in_module__(
    *,
    name: str,
    obtaining_function: Callable[[], str],
    conversion_function: Callable[[str], Any] | type,
    validator_function: Callable[[Any], bool],
    reobtain_each_usage: bool,
    module_ref: FrameType,
) -> None:
    module_ref.f_globals[name] = __returnable_value__(
        obtaining_function=obtaining_function,
        conversion_function=conversion_function,
        validator_function=validator_function,
        reobtain_each_usage=reobtain_each_usage,
    )


@validate_call
def __generate_obtain_secret_function__(
    store_name: str,
    name_in_store: str,
    default: str | None = None,
) -> Callable[[], str]:
    @validate_call
    def obtain_secret() -> str:
        return keyring.get_password(store_name, name_in_store) or default  # type: ignore  # noqa: PGH003

    return obtain_secret


@validate_call
def __generate_obtain_env_val_function__(
    name: str,
    default: str | None = None,
) -> Callable[[], str]:
    @validate_call
    def obtaining_function() -> str:
        val = environ.get(name, default)
        if val is None:
            raise SettingsNotFoundError(f"Environment variable {name} is required but not set.")
        return val

    return obtaining_function


@validate_call
def __set_var_in_calling_module__(
    name: str,
    obtaining_function: Callable[[], str],
    conversion_function: Callable[[str], Any] | type,
    validator_function: Callable[[Any], bool],
    reobtain_each_usage: bool,
) -> None:
    __set_in_module__(
        name=name,
        obtaining_function=obtaining_function,
        validator_function=validator_function,
        reobtain_each_usage=reobtain_each_usage,
        conversion_function=conversion_function,
        module_ref=__get_calling_module__(),
    )


@validate_call
def __set_var_in_python_settings__(
    name: str,
    obtaining_function: Callable[[], str],
    conversion_function: Callable[[str], Any] | type,
    validator_function: Callable[[Any], bool],
    reobtain_each_usage: bool,
) -> None:
    __set_in_module__(
        name=name,
        obtaining_function=obtaining_function,
        validator_function=validator_function,
        reobtain_each_usage=reobtain_each_usage,
        conversion_function=conversion_function,
        module_ref=__get_this_module__(),
    )


@validate_call
def track_env_var(
    env_var_name: str,
    default: str | None = None,
    validator_function: Callable[[Any], bool] = lambda _: True,
    reobtain_each_usage: bool = False,
    conversion_function: Callable[[str], Any] | type = str,
) -> None:
    """
    Set a variable in the calling module with the same name as the environment variable given as `name`.

    Parameters
    ----------
    env_var_name : str
        Name of an environmental variable to obtain the value of.
    default : str or None, optional
        If not None, a default value to use if the environmental value specified by env_var_name is not set.
    validator_function : callable, optional
        An additional validation function to accept or reject the obtained value.
    reobtain_each_usage : bool, optional
        If true, on each access reobtain the value. If not, it is only obtained once when this function is
        called.
    conversion_function : callable or type, optional
        A function or type that converts the obtained value to the desired type.

    Returns
    -------
    None
        This function does not return anything. It sets a variable in the calling module as a side effect.

    """
    __set_var_in_python_settings__(
        name=env_var_name,
        obtaining_function=__generate_obtain_env_val_function__(env_var_name, default),
        validator_function=validator_function,
        reobtain_each_usage=reobtain_each_usage,
        conversion_function=conversion_function,
    )


@validate_call
def track_secret_var(
    var_name: str,
    store_name: str,
    name_in_store: str,
    default: str | None = None,
    validator_function: Callable[[Any], bool] = lambda _: True,
    reobtain_each_usage: bool = True,
    conversion_function: Callable[[str], Any] | type = str,
) -> None:
    """
    Get a secret from a secret store (and help set if missing and no default is provided).

    To understand better, here's an example from the CLI:
        Set:
            `python -m keyring -b keyring.backends.SecretService.Keyring set Passwords pythonkeyringcli`
            -> asks for password
        Get:
            `python -m keyring -b keyring.backends.SecretService.Keyring get Passwords pythonkeyringcli`
            -> prints password

    And in your passwords manager, in my case Wallet Manager, this appears under the
    tree as:
    "Secret Service" -> "Passwords" -> "Password for 'pythonkeyringcli' on 'Passwords'"

    But you'll notice that you can't retrieve all your other passwords. This is a
    security feature. Only passwords a program has set can be retrieved by that
    program. However, this can become finicky. This is a trade-off.

    .. warning::
        You may have to use `sey_keyring()` if the correct backend is not
        automatically set.
        Please refer to https://pypi.org/project/keyring/ for more information.

    Parameters
    ----------
    var_name : str
        The name of the variable to get and set.
    store_name : str
        The name of the secret store to get the secret from.
    name_in_store : str
        The name of the secret in the secret store.
    default : str or None, optional
        The default value to use if the secret is not set.
    validator_function : callable, optional
        An auxiliary function that validates the value according to user specified criteria.
    reobtain_each_usage : bool, optional
        If True, the value will be reobtained each time it is used. If False, the value will be
        obtained once and then reused. Set to True if the value changes during runtime and the
        program needs the updated value in order to operate correctly. For security reasons,
        it is recommended to set this to True.
    conversion_function : callable or type, optional
        An auxiliary function that converts the value from a string to the desired type.
        Use this for complex or nested types.

    Returns
    -------
    None
        This function does not return anything. It sets a variable in the calling
        module as a side effect.

    """
    __set_var_in_python_settings__(
        name=var_name,
        obtaining_function=__generate_obtain_secret_function__(
            store_name=store_name,
            name_in_store=name_in_store,
            default=default,
        ),
        validator_function=validator_function,
        reobtain_each_usage=reobtain_each_usage,
        conversion_function=conversion_function,
    )


@validate_call
def set_env_var_locally(
    name: str,
    default: str | None = None,
    validator_function: Callable[[Any], bool] = lambda _: True,
    reobtain_each_usage: bool = False,
    conversion_function: Callable[[str], Any] | type = str,
) -> None:
    """
    Set a variable in the calling module with the same name as the environment variable given as `name`.

    Parameters
    ----------
    name : str
        The name of the environment variable to get and set.
    default : str or None, optional
        The default value to use if the environment variable is not set.
    validator_function : callable, optional
        An auxiliary function that validates the value according to user specified criteria.
    reobtain_each_usage : bool, optional
        If True, the value will be reobtained each time it is used. If False, the value will be
        obtained once and then reused. Set to True if the value changes during runtime and the
        program needs the updated value in order to operate correctly. For security reasons,
        it is recommended to set this to True.
    conversion_function : callable or type, optional
        An auxiliary function that converts the value from a string to the desired type.
        Use this for complex or nested types.

    Returns
    -------
    None
        This function does not return anything. It sets a variable in the calling module as a side effect.

    """
    __set_var_in_calling_module__(
        name=name,
        obtaining_function=__generate_obtain_env_val_function__(name, default),
        validator_function=validator_function,
        reobtain_each_usage=reobtain_each_usage,
        conversion_function=conversion_function,
    )


@validate_call
def set_secret_var_locally(
    var_name: str,
    store_name: str,
    name_in_store: str,
    default: str | None = None,
    validator_function: Callable[[Any], bool] = lambda _: True,
    reobtain_each_usage: bool = True,
    conversion_function: Callable[[str], Any] | type = str,
) -> None:
    """
    Get a secret from a secret store (and help set if missing and no default is provided).

    To understand better, here's an example from the CLI:
        Set:
            `python -m keyring -b keyring.backends.SecretService.Keyring set Passwords pythonkeyringcli`
            -> asks for password
        Get:
            `python -m keyring -b keyring.backends.SecretService.Keyring get Passwords pythonkeyringcli`
            -> prints password

    And in your passwords manager, in my case Wallet Manager, this appears under the
    tree as:
    "Secret Service" -> "Passwords" -> "Password for 'pythonkeyringcli' on 'Passwords'"

    But you'll notice that you can't retrieve all your other passwords. This is a
    security feature. Only passwords a program has set can be retrieved by that
    program. However, this can become finicky. This is a trade-off.

    .. warning::
        You may have to use `sey_keyring()` if the correct backend is not
        automatically set.
        Please refer to https://pypi.org/project/keyring/ for more information.

    Parameters
    ----------
    var_name : str
        The name of the variable to get and set in the calling module.
    store_name : str
        The name of the secret store to get the secret from.
    name_in_store : str
        The name of the secret in the secret store.
    default : str or None, optional
        The default value to use if the secret is not set.
    validator_function : callable, optional
        An auxiliary function that validates the value according to user specified criteria.
    reobtain_each_usage : bool, optional
        If True, the value will be reobtained each time it is used. If False, the value will be
        obtained once and then reused. Set to True if the value changes during runtime and the
        program needs the updated value in order to operate correctly. For security reasons,
        it is recommended to set this to True.
    conversion_function : callable or type, optional
        An auxiliary function that converts the value from a string to the desired type.
        Use this for complex or nested types.

    Returns
    -------
    None
        This function does not return anything. It sets a variable in the calling
        module as a side effect.

    """
    __set_var_in_calling_module__(
        name=var_name,
        obtaining_function=__generate_obtain_secret_function__(
            store_name=store_name,
            name_in_store=name_in_store,
            default=default,
        ),
        validator_function=validator_function,
        reobtain_each_usage=reobtain_each_usage,
        conversion_function=conversion_function,
    )


def return_env_var(
    env_var_name: str,
    default: str | None = None,
    validator_function: Callable[[Any], bool] = lambda _: True,
    reobtain_each_usage: bool = False,
    conversion_function: Callable[[str], Any] | type = str,
) -> Any:
    """
    Get a value from an environment variable.

    Parameters
    ----------
    env_var_name : str
        The name of the environment variable to get.
    default : str or None, optional
        The default value to use if the environment variable is not set.
    validator_function : callable, optional
        An auxiliary function that validates the value according to user specified criteria.
    reobtain_each_usage : bool, optional
        If True, the value will be reobtained each time it is used. If False, the value will be
        obtained once and then reused. Set to True if the value changes during runtime and the
        program needs the updated value in order to operate correctly.
    conversion_function : callable or type, optional
        An auxiliary function that converts the value from a string to the desired type.
        Use this for complex or nested types.

    Returns
    -------
    Any
        The value of the environment variable.

    """
    return __returnable_value__(
        obtaining_function=__generate_obtain_env_val_function__(env_var_name, default),
        conversion_function=conversion_function,
        validator_function=validator_function,
        reobtain_each_usage=reobtain_each_usage,
    )


def return_secret_var(
    store_name: str,
    name_in_store: str,
    default: str | None = None,
    validator_function: Callable[[Any], bool] = lambda _: True,
    reobtain_each_usage: bool = True,
    conversion_function: Callable[[str], Any] | type = str,
) -> Any:
    """
    Get a secret from a secret store (and help set if missing and no default is provided).

    To understand better, here's an example from the CLI:
        Set:
            `python -m keyring -b keyring.backends.SecretService.Keyring set Passwords pythonkeyringcli`
            -> asks for password
        Get:
            `python -m keyring -b keyring.backends.SecretService.Keyring get Passwords pythonkeyringcli`
            -> prints password

    And in your passwords manager, in my case Wallet Manager, this appears under the
    tree as:
    "Secret Service" -> "Passwords" -> "Password for 'pythonkeyringcli' on 'Passwords'"

    But you'll notice that you can't retrieve all your other passwords. This is a
    security feature. Only passwords a program has set can be retrieved by that
    program. However, this can become finicky. This is a trade-off.

    .. warning::
        You may have to use `sey_keyring()` if the correct backend is not
        automatically set.
        Please refer to https://pypi.org/project/keyring/ for more information.

    Parameters
    ----------
    store_name : str
        The name of the secret store to get the secret from.
    name_in_store : str
        The name of the secret in the secret store.
    default : str or None, optional
        The default value to use if the secret is not set.
    validator_function : callable, optional
        An auxiliary function that validates the value according to user specified criteria.
    reobtain_each_usage : bool, optional
        If True, the value will be reobtained each time it is used. If False, the value will be
        obtained once and then reused. Set to True if the value changes during runtime and the
        program needs the updated value in order to operate correctly. For security reasons,
        it is recommended to set this to True.
    conversion_function : callable or type, optional
        An auxiliary function that converts the value from a string to the desired type.
        Use this for complex or nested types.

    Returns
    -------
    Any
        The retrieved secret value after any conversion has been applied.

    """
    return __returnable_value__(
        obtaining_function=__generate_obtain_secret_function__(
            store_name=store_name,
            name_in_store=name_in_store,
            default=default,
        ),
        conversion_function=conversion_function,
        reobtain_each_usage=reobtain_each_usage,
        validator_function=validator_function,
    )
