"""Core functions for SFS Settings.  Not for public use."""

from __future__ import annotations

from collections.abc import Callable
from os import environ
from types import ModuleType
from typing import Any

import keyring
from pydantic import validate_call

from sfs_settings.exceptions import SettingsNotFoundError
from sfs_settings.pseudo_variable import PseudoVariable
from sfs_settings.utility_functions import get_calling_module, get_this_module, obtain_convert_and_validate


def set_in_module(
    *,
    name: str,
    obtaining_function: Callable[[], str],
    conversion_function: Callable[[str], Any] | type,
    validator_function: Callable[[Any], bool],
    reobtain_each_usage: bool,
    module_ref: ModuleType,
) -> None:
    """Set a variable in a module."""
    setattr(
        module_ref,
        name,
        returnable_value(
            obtaining_function=obtaining_function,
            conversion_function=conversion_function,
            validator_function=validator_function,
            reobtain_each_usage=reobtain_each_usage,
        ),
    )


@validate_call
def returnable_value(
    *,
    obtaining_function: Callable[[], str],
    conversion_function: Callable[[str], Any] | type,
    validator_function: Callable[[Any], bool],
    reobtain_each_usage: bool,
) -> Any:
    """Return a value that can be used as a variable."""
    return (
        PseudoVariable(
            obtaining_function=obtaining_function,
            conversion_function=conversion_function,
            validator_function=validator_function,
        )
        if reobtain_each_usage
        else obtain_convert_and_validate(
            obtaining_function=obtaining_function,
            conversion_function=conversion_function,
            is_valid_function=validator_function,
        )
    )


@validate_call
def generate_obtain_secret_function(
    store_name: str,
    name_in_store: str,
    default: str | None = None,
) -> Callable[[], str]:
    """Generate a function that obtains a secret from a secret store."""

    @validate_call
    def obtain_secret() -> str:
        """Obtain the secret from the secret store."""
        return keyring.get_password(store_name, name_in_store) or default  # type: ignore  # noqa: PGH003

    return obtain_secret


@validate_call
def generate_obtain_env_val_function(
    name: str,
    default: str | None = None,
) -> Callable[[], str]:
    """Generate a function that obtains an environment variable."""

    @validate_call
    def obtaining_function() -> str:
        """Obtain the environment variable."""
        val = environ.get(name, default)
        if val is None:
            raise SettingsNotFoundError(f"Environment variable {name} is required but not set.")
        return val

    return obtaining_function


@validate_call
def set_var_in_calling_module(
    name: str,
    obtaining_function: Callable[[], str],
    conversion_function: Callable[[str], Any] | type,
    validator_function: Callable[[Any], bool],
    reobtain_each_usage: bool,
) -> None:
    """Set a variable in the calling module."""
    set_in_module(
        name=name,
        obtaining_function=obtaining_function,
        validator_function=validator_function,
        reobtain_each_usage=reobtain_each_usage,
        conversion_function=conversion_function,
        module_ref=get_calling_module(),
    )


@validate_call
def set_var_in_sfs_settings(
    name: str,
    obtaining_function: Callable[[], str],
    conversion_function: Callable[[str], Any] | type,
    validator_function: Callable[[Any], bool],
    reobtain_each_usage: bool,
) -> None:
    """Set a variable in the sfs_settings module."""
    set_in_module(
        name=name,
        obtaining_function=obtaining_function,
        validator_function=validator_function,
        reobtain_each_usage=reobtain_each_usage,
        conversion_function=conversion_function,
        module_ref=get_this_module(),
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
    default : str or None, Optional
        If not None, a default value to use if the environmental value specified by env_var_name is not set.
    validator_function : Callable[[Any], bool], Optional
        An additional validation function to accept or reject the obtained value.
    reobtain_each_usage : bool, Optional
        If true, on each access reobtain the value. If not, it is only obtained once when this function is
        called.
    conversion_function : Callable[[str], Any] or type, Optional
        A function or type that converts the obtained value to the desired type.

    Returns
    -------
    None
        This function does not return anything. It sets a variable in the calling module as a side effect.

    """
    set_var_in_sfs_settings(
        name=env_var_name,
        obtaining_function=generate_obtain_env_val_function(env_var_name, default),
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
    default : str or None, Optional
        The default value to use if the secret is not set.
    validator_function : Callable[[Any], bool], Optional
        An auxiliary function that validates the value according to user specified criteria.
    reobtain_each_usage : bool, Optional
        If True, the value will be reobtained each time it is used. If False, the value will be
        obtained once and then reused. Set to True if the value changes during runtime and the
        program needs the updated value in order to operate correctly. For security reasons,
        it is recommended to set this to True.
    conversion_function : Callable[[str], Any] or type, Optional
        An auxiliary function that converts the value from a string to the desired type.
        Use this for complex or nested types.

    Returns
    -------
    None
        This function does not return anything. It sets a variable in the calling
        module as a side effect.

    """
    set_var_in_sfs_settings(
        name=var_name,
        obtaining_function=generate_obtain_secret_function(
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
    default : str or None, Optional
        The default value to use if the environment variable is not set.
    validator_function : Callable[[Any], bool], Optional
        An auxiliary function that validates the value according to user specified criteria.
    reobtain_each_usage : bool, Optional
        If True, the value will be reobtained each time it is used. If False, the value will be
        obtained once and then reused. Set to True if the value changes during runtime and the
        program needs the updated value in order to operate correctly. For security reasons,
        it is recommended to set this to True.
    conversion_function : Callable[[str], Any] or type, Optional
        An auxiliary function that converts the value from a string to the desired type.
        Use this for complex or nested types.

    Returns
    -------
    None
        This function does not return anything. It sets a variable in the calling module as a side effect.

    """
    set_var_in_calling_module(
        name=name,
        obtaining_function=generate_obtain_env_val_function(name, default),
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
    default : str or None, Optional
        The default value to use if the secret is not set.
    validator_function : Callable[[Any], bool], Optional
        An auxiliary function that validates the value according to user specified criteria.
    reobtain_each_usage : bool, Optional
        If True, the value will be reobtained each time it is used. If False, the value will be
        obtained once and then reused. Set to True if the value changes during runtime and the
        program needs the updated value in order to operate correctly. For security reasons,
        it is recommended to set this to True.
    conversion_function : Callable[[str], Any] or type, Optional
        An auxiliary function that converts the value from a string to the desired type.
        Use this for complex or nested types.

    Returns
    -------
    None
        This function does not return anything. It sets a variable in the calling
        module as a side effect.

    """
    set_var_in_calling_module(
        name=var_name,
        obtaining_function=generate_obtain_secret_function(
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
    default : str or None, Optional
        The default value to use if the environment variable is not set.
    validator_function : Callable[[Any], bool], Optional
        An auxiliary function that validates the value according to user specified criteria.
    reobtain_each_usage : bool, Optional
        If True, the value will be reobtained each time it is used. If False, the value will be
        obtained once and then reused. Set to True if the value changes during runtime and the
        program needs the updated value in order to operate correctly.
    conversion_function : Callable[[str], Any] or type, Optional
        An auxiliary function that converts the value from a string to the desired type.
        Use this for complex or nested types.

    Returns
    -------
    Any
        The value of the environment variable.

    """
    return returnable_value(
        obtaining_function=generate_obtain_env_val_function(env_var_name, default),
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
    default : str or None, Optional
        The default value to use if the secret is not set.
    validator_function : Callable[[Any], bool], Optional
        An auxiliary function that validates the value according to user specified criteria.
    reobtain_each_usage : bool, Optional
        If True, the value will be reobtained each time it is used. If False, the value will be
        obtained once and then reused. Set to True if the value changes during runtime and the
        program needs the updated value in order to operate correctly. For security reasons,
        it is recommended to set this to True.
    conversion_function : Callable[[str], Any] or type, Optional
        An auxiliary function that converts the value from a string to the desired type.
        Use this for complex or nested types.

    Returns
    -------
    Any
        The retrieved secret value after any conversion has been applied.

    """
    return returnable_value(
        obtaining_function=generate_obtain_secret_function(
            store_name=store_name,
            name_in_store=name_in_store,
            default=default,
        ),
        conversion_function=conversion_function,
        reobtain_each_usage=reobtain_each_usage,
        validator_function=validator_function,
    )
