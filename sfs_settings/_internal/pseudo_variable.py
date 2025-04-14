"""Pseudo variable class."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pydantic import validate_call

from sfs_settings._internal._funcs import obtain_convert_and_validate


class PseudoVariable:
    """
    Later on, replace this mechanism with __getattr__.
    Has imperfect security due to underlying python characteristics.  These can't be further improved.
    """

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
        return obtain_convert_and_validate(
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
