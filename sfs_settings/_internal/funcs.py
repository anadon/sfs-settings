from __future__ import annotations

from collections.abc import Callable
from os import environ
from types import FrameType
from typing import Any

import keyring
from pydantic import validate_call

from sfs_settings._internal._funcs import get_calling_module, get_this_module, obtain_convert_and_validate
from sfs_settings._internal.pseudo_variable import PseudoVariable
from sfs_settings._internal.sfs_settings_exceptions import SettingsNotFoundError


def set_in_module(
    *,
    name: str,
    obtaining_function: Callable[[], str],
    conversion_function: Callable[[str], Any] | type,
    validator_function: Callable[[Any], bool],
    reobtain_each_usage: bool,
    module_ref: FrameType,
) -> None:
    module_ref.f_globals[name] = returnable_value(
        obtaining_function=obtaining_function,
        conversion_function=conversion_function,
        validator_function=validator_function,
        reobtain_each_usage=reobtain_each_usage,
    )


@validate_call
def returnable_value(
    *,
    obtaining_function: Callable[[], str],
    conversion_function: Callable[[str], Any] | type,
    validator_function: Callable[[Any], bool],
    reobtain_each_usage: bool,
) -> Any:
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
    @validate_call
    def obtain_secret() -> str:
        return keyring.get_password(store_name, name_in_store) or default  # type: ignore  # noqa: PGH003

    return obtain_secret


@validate_call
def generate_obtain_env_val_function(
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
def set_var_in_calling_module(
    name: str,
    obtaining_function: Callable[[], str],
    conversion_function: Callable[[str], Any] | type,
    validator_function: Callable[[Any], bool],
    reobtain_each_usage: bool,
) -> None:
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
    set_in_module(
        name=name,
        obtaining_function=obtaining_function,
        validator_function=validator_function,
        reobtain_each_usage=reobtain_each_usage,
        conversion_function=conversion_function,
        module_ref=get_this_module(),
    )
