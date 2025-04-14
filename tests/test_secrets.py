# ruff: noqa: PT011, D103, ANN201, PLR2004, S101, PLW0602, D100, D104
from __future__ import annotations

import random
import string
from typing import Any
from unittest.mock import patch

import pytest

import sfs_settings as sfs
from sfs_settings import (
    SettingsValidationError,
    return_secret_var,
    set_secret_var_locally,
    track_secret_var,
)

STORE_NAME = "test_store"
KEY_NAME = "test_key"

SECRET = str("".join(random.choice(string.hexdigits) for _ in range(16)))  # noqa: S311

# Secret Management Tests


def fake(_x: Any, _y: Any) -> str:
    global SECRET
    return SECRET


@patch("keyring.get_password", fake)
def test_secret_get_lazy_local() -> None:
    """Test secret deletion behavior."""
    global TEMP_KEY, STORE_NAME, KEY_NAME, SECRET

    set_secret_var_locally("TEMP_KEY", STORE_NAME, KEY_NAME)

    assert (
        SECRET == TEMP_KEY  # type: ignore[name-defined, attr-defined]
    ), f"TEMP_KEY is not set to the secret value, but is set to {TEMP_KEY!s}"  # type: ignore[name-defined, attr-defined]


@patch("keyring.get_password", fake)
def test_secret_get_lazy_tracked() -> None:
    """Test secret deletion behavior."""
    global STORE_NAME, KEY_NAME, SECRET

    track_secret_var("TEMP_KEY", STORE_NAME, KEY_NAME)

    assert (
        SECRET.__str__() == sfs.TEMP_KEY.__str__()  # type: ignore[name-defined, attr-defined]
    ), f"TEMP_KEY is not set to the secret value, but is set to {sfs.TEMP_KEY!s}"  # type: ignore[name-defined, attr-defined]


@patch("keyring.get_password", fake)
def test_secret_get_lazy_returned() -> None:
    """Test secret deletion behavior."""
    global STORE_NAME, KEY_NAME, SECRET

    temp_key = return_secret_var(STORE_NAME, KEY_NAME)

    assert temp_key.__repr__() == repr(SECRET), (
        f"TEMP_KEY is not set to {SECRET!r}, but is set to {temp_key.__repr__()!r}"
    )


@patch("keyring.get_password", fake)
def test_secret_get_immediate_local() -> None:
    """Test secret deletion behavior."""
    global TEMP_KEY, STORE_NAME, KEY_NAME

    set_secret_var_locally("TEMP_KEY", STORE_NAME, KEY_NAME, reobtain_each_usage=False)

    assert (
        SECRET == TEMP_KEY  # type: ignore[name-defined, attr-defined]
    ), f"TEMP_KEY is not set to the secret value, but is set to {TEMP_KEY!s}"  # type: ignore[name-defined, attr-defined]


@patch("keyring.get_password", fake)
def test_secret_get_immediate_tracked() -> None:
    """Test secret deletion behavior."""
    global STORE_NAME, KEY_NAME, SECRET

    track_secret_var("TEMP_KEY", STORE_NAME, KEY_NAME, reobtain_each_usage=False)

    assert (
        SECRET == sfs.TEMP_KEY  # type: ignore[name-defined, attr-defined]
    ), f"TEMP_KEY is not set to the secret value, but is set to {sfs.TEMP_KEY!s}"  # type: ignore[name-defined, attr-defined]


@patch("keyring.get_password", fake)
def test_secret_get_immediate_returned() -> None:
    """Test secret deletion behavior."""
    global STORE_NAME, KEY_NAME, SECRET

    temp_key = return_secret_var(STORE_NAME, KEY_NAME, reobtain_each_usage=False)

    assert temp_key == SECRET, f"TEMP_KEY is not set to the secret value, but is set to {temp_key!s}"


@patch("keyring.get_password", fake)
def test_secret_validation() -> None:
    """Test secret value validation."""
    global API_KEY, STORE_NAME, KEY_NAME

    set_secret_var_locally("API_KEY", STORE_NAME, KEY_NAME, validator_function=lambda x: len(x) > 100)
    with pytest.raises(SettingsValidationError):
        API_KEY()  # type: ignore[name-defined, attr-defined]


def test_secret_rotation() -> None:
    """Test that secrets are re-obtained when reobtain_each_usage is True."""
    global ROTATING_KEY, STORE_NAME, KEY_NAME

    set_secret_var_locally("ROTATING_KEY", STORE_NAME, KEY_NAME)
    with patch("keyring.get_password", return_value="old_secret"):
        old_key = ROTATING_KEY()  # type: ignore[name-defined, attr-defined]
    assert old_key == "old_secret"

    with patch("keyring.get_password", return_value="new_secret"):
        new_key = ROTATING_KEY()  # type: ignore[name-defined, attr-defined]
    assert old_key == "old_secret"
    assert new_key == "new_secret"
