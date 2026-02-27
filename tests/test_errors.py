"""Tests for EZRA exception hierarchy.

This module verifies that the typed exception hierarchy is correctly
structured and that dual inheritance preserves stdlib compatibility.
"""

from __future__ import annotations

import pytest

from ezra.errors import (
    EPBCanonicalError,
    EPBError,
    EPBHashError,
    EPBValidationError,
    EzraError,
    PluginError,
    PluginExecutionError,
    PluginRegistryError,
    PluginResolutionError,
    ZoneSchemaError,
)


def test_ezra_error_is_base_class() -> None:
    """Test that EzraError is the root of the hierarchy."""
    assert issubclass(PluginError, EzraError)
    assert issubclass(EPBError, EzraError)
    assert issubclass(ZoneSchemaError, EzraError)


def test_plugin_error_hierarchy() -> None:
    """Test PluginError subclasses."""
    assert issubclass(PluginRegistryError, PluginError)
    assert issubclass(PluginResolutionError, PluginError)
    assert issubclass(PluginExecutionError, PluginError)


def test_epb_error_hierarchy() -> None:
    """Test EPBError subclasses."""
    assert issubclass(EPBValidationError, EPBError)
    assert issubclass(EPBHashError, EPBError)
    assert issubclass(EPBCanonicalError, EPBError)


def test_dual_inheritance_valueerror() -> None:
    """Test that exceptions dual-inherit from ValueError where appropriate."""
    assert issubclass(EPBValidationError, ValueError)
    assert issubclass(EPBHashError, ValueError)
    assert issubclass(EPBCanonicalError, ValueError)
    assert issubclass(PluginResolutionError, ValueError)
    assert issubclass(ZoneSchemaError, ValueError)


def test_dual_inheritance_typeerror() -> None:
    """Test that PluginRegistryError dual-inherits from TypeError."""
    assert issubclass(PluginRegistryError, TypeError)


def test_dual_inheritance_runtimeerror() -> None:
    """Test that PluginExecutionError dual-inherits from RuntimeError."""
    assert issubclass(PluginExecutionError, RuntimeError)


def test_exception_instances_are_catchable_by_stdlib() -> None:
    """Test that typed exceptions can be caught by stdlib exception types."""
    # EPBValidationError should be catchable as ValueError
    try:
        raise EPBValidationError("test")
    except ValueError:
        pass
    else:
        pytest.fail("EPBValidationError not catchable as ValueError")

    # PluginRegistryError should be catchable as TypeError
    try:
        raise PluginRegistryError("test")
    except TypeError:
        pass
    else:
        pytest.fail("PluginRegistryError not catchable as TypeError")

    # PluginExecutionError should be catchable as RuntimeError
    try:
        raise PluginExecutionError("test")
    except RuntimeError:
        pass
    else:
        pytest.fail("PluginExecutionError not catchable as RuntimeError")

    # All should be catchable as EzraError
    try:
        raise EPBValidationError("test")
    except EzraError:
        pass
    else:
        pytest.fail("EPBValidationError not catchable as EzraError")

    try:
        raise PluginResolutionError("test")
    except EzraError:
        pass
    else:
        pytest.fail("PluginResolutionError not catchable as EzraError")

    try:
        raise ZoneSchemaError("test")
    except EzraError:
        pass
    else:
        pytest.fail("ZoneSchemaError not catchable as EzraError")


def test_exception_messages_preserved() -> None:
    """Test that exception messages are preserved."""
    msg = "Test error message"
    exc = EPBValidationError(msg)
    assert str(exc) == msg

    exc = PluginResolutionError(msg)
    assert str(exc) == msg

    exc = ZoneSchemaError(msg)
    assert str(exc) == msg

