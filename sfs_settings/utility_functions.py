"""Utility functions for SFS Settings.  Not for public use."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from types import ModuleType
from typing import Any

from pydantic import validate_call

import sfs_settings
from sfs_settings.exceptions import SettingsValidationError


@validate_call
def obtain_convert_and_validate(
    *,
    obtaining_function: Callable[[], str],
    conversion_function: Callable[[str], Any] | type,
    is_valid_function: Callable[[Any], bool] = lambda _: True,
) -> Any:
    """Obtain, convert, and validate a value."""
    value = obtaining_function()
    converted_value = conversion_function(value) if value is not None else None
    if not is_valid_function(converted_value):
        raise SettingsValidationError
    return converted_value


def get_calling_module() -> ModuleType:
    """Get the module that called the function.  Kinda hacky."""
    for frame in inspect.stack():
        if not (set(frame.filename.split("/")) & {"sfs_settings", "pydantic"}):
            return inspect.getmodule(frame.frame)  # type: ignore[return-value]
    raise ValueError(  # pragma: no cover
        "Could not find calling module.  This should be impossible.  Unreachable statement reached."
    )


def get_this_module() -> ModuleType:
    """Get the module that contains the function.  Kinda hacky."""
    return sfs_settings
