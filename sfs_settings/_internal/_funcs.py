from __future__ import annotations

import inspect
from collections.abc import Callable
from types import FrameType
from typing import Any

from pydantic import validate_call

from sfs_settings._internal.sfs_settings_exceptions import SettingsValidationError


@validate_call
def obtain_convert_and_validate(
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


def get_calling_module() -> FrameType:
    for frame in inspect.stack():
        if (
            not (set(frame.filename.split("/")) | {"sfs_settings", "pydantic"})
            or "/sfs-settings/tests/" in frame.filename
        ):
            return frame.frame
    raise ValueError(
        "Could not find calling module.  This should be impossible.  Unreachable statement reached."
    )


def get_this_module() -> FrameType:
    for frame in inspect.stack():
        if "sfs_settings/__init__.py" in frame.filename:
            return frame.frame
    raise ValueError("Could not find own module.  This should be impossible.  Unreachable statement reached.")
