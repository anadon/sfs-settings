# ruff: noqa: PT011, D103, ANN201, PLR2004, S101, PLW0602, D100, D104
from __future__ import annotations

import os
import random
import string
import sys  # Add missing import
from typing import Any
from unittest.mock import patch

import pytest

import sfs_settings as sfs
from sfs_settings.core_functions import (
    return_env_var,
    set_env_var_locally,
    track_env_var,
)
from sfs_settings.exceptions import SettingsNotFoundError


class TestEnvironmentVariables:
    """Test suite for environment variables."""

    def test_invalid_type_conversion(self) -> None:
        """Test handling of invalid type conversion."""
        with patch.dict(os.environ, {"NUMBER": "not_a_number"}), pytest.raises(ValueError):
            set_env_var_locally("NUMBER", conversion_function=int)

    def test_validation_chain(self) -> None:
        """Test multiple validation stesfs."""
        global VALID_VAR, INVALID_VAR

        def validate_length(x: str) -> bool:
            return len(x) >= 8

        def validate_prefix(x: str) -> bool:
            return x.startswith("test_")

        def validate_all(x: str) -> bool:
            return validate_length(x) and validate_prefix(x)

        with patch.dict(os.environ, {"VALID_VAR": "test_12345"}):
            set_env_var_locally("VALID_VAR", validator_function=validate_all)
            assert VALID_VAR == "test_12345"  # type: ignore[name-defined, attr-defined]

        with patch.dict(os.environ, {"INVALID_VAR": "bad"}), pytest.raises(ValueError):
            set_env_var_locally("INVALID_VAR", validator_function=validate_all)


# Complex Type Conversion Tests
class TestTypeConversion:
    """Test suite for type conversion functionality."""

    def test_custom_type_handling(self) -> None:
        """Test conversion to custom types."""

        class CustomType:
            def __init__(self, value: int) -> None:
                self.value = value

            @classmethod
            def from_string(cls, s: str) -> CustomType:
                return cls(int(s))


def test_missing_env_var_without_default():
    """Test handling of missing environment variables."""
    with pytest.raises(SettingsNotFoundError):
        _ = return_env_var("MISSING_VAR")


# Cleanup fixture
@pytest.fixture(autouse=True)
def cleanup_environment():
    """Clean up environment variables and sys.modules after each test."""
    original_environ = dict(os.environ)
    original_modules = dict(sys.modules)

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_environ)

    # Restore original modules
    for mod in set(sys.modules) - set(original_modules):
        del sys.modules[mod]


RAND_VAL = "".join(random.choice(string.hexdigits) for _ in range(16))  # noqa: S311


def fake(*_: Any) -> str:
    global RAND_VAL
    return RAND_VAL


@patch("os.environ.get", fake)
def test_env_get_lazy_local() -> None:
    """Test environment variable retrieval for lazy retrieval from locally set value."""
    global TEMP_KEY, RAND_VAL

    set_env_var_locally("TEMP_KEY")
    assert (
        TEMP_KEY == RAND_VAL  # type: ignore[name-defined, attr-defined]
    ), f"TEMP_KEY is not set to {RAND_VAL}, but is set to {TEMP_KEY!s}"  # type: ignore[name-defined, attr-defined]


@patch("os.environ.get", fake)
def test_env_get_lazy_tracked() -> None:
    """Test environment variable retrieval for lazy retrieval from sfs_settings."""
    global TEMP_KEY, RAND_VAL
    track_env_var("TEMP_KEY")
    assert (
        sfs.TEMP_KEY == RAND_VAL  # type: ignore[name-defined, attr-defined]
    ), f"TEMP_KEY is not set to {RAND_VAL}, but is set to {sfs.TEMP_KEY!s}"  # type: ignore[name-defined, attr-defined]


@patch("os.environ.get", fake)
def test_env_get_lazy_returned() -> None:
    """Test environment variable retrieval for lazy retrieval from returned value."""
    global RAND_VAL
    temp_key = return_env_var("TEMP_KEY")
    assert temp_key == RAND_VAL, f"TEMP_KEY is not set to {RAND_VAL}, but is set to {temp_key!s}"
