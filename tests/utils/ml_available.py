"""Helpers for checking optional ML dependency availability in tests."""

from __future__ import annotations

import importlib.util


def has_easyocr() -> bool:
    """Return True when easyocr can be imported in current environment."""
    return importlib.util.find_spec("easyocr") is not None


def has_torch() -> bool:
    """Return True when torch can be imported in current environment."""
    return importlib.util.find_spec("torch") is not None
