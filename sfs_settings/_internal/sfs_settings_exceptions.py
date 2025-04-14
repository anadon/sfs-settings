"""Exceptions for sfs_settings."""

from __future__ import annotations


class SettingsValidationError(ValueError):
    """Raised when a setting fails validation."""


class SettingsNotFoundError(ValueError):
    """Raised when a required setting is not found."""
