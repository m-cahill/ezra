"""EZRA runtime exception hierarchy.

This module defines a typed exception taxonomy for EZRA runtime failures.
All exceptions dual-inherit from both EzraError (EZRA taxonomy root) and
the closest equivalent stdlib exception type for backward compatibility.
"""

from __future__ import annotations


class EzraError(Exception):
    """Base class for all EZRA runtime errors.

    All EZRA-specific exceptions inherit from this class, providing a
    single catch point for EZRA-originated failures.
    """


class PluginError(EzraError):
    """Base class for plugin-level failures."""

    pass


class PluginRegistryError(PluginError, TypeError):
    """Registry format or entry validation failure.

    Raised when plugin registry entries are malformed or invalid.
    Dual-inherits from TypeError to preserve stdlib compatibility.
    """

    pass


class PluginResolutionError(PluginError, ValueError):
    """Plugin resolution failure.

    Raised when a plugin cannot be resolved (e.g., unknown plugin name).
    Dual-inherits from ValueError to preserve stdlib compatibility.
    """

    pass


class PluginExecutionError(PluginError, RuntimeError):
    """Plugin execution failure.

    Raised when plugin inference or model loading fails.
    Dual-inherits from RuntimeError to preserve stdlib compatibility.
    """

    pass


class EPBError(EzraError):
    """Base class for EPB bundle construction failures."""

    pass


class EPBValidationError(EPBError, ValueError):
    """EPB schema validation failure.

    Raised when EPB bundle components fail JSON Schema validation.
    Dual-inherits from ValueError to preserve stdlib compatibility.
    """

    pass


class EPBHashError(EPBError, ValueError):
    """EPB hash mismatch or verification failure.

    Raised when EPB bundle hash verification fails or hashes are missing.
    Dual-inherits from ValueError to preserve stdlib compatibility.
    """

    pass


class EPBCanonicalError(EPBError, ValueError):
    """EPB canonicalization failure.

    Raised when EPB bundle contains non-canonical values (NaN, Infinity).
    Dual-inherits from ValueError to preserve stdlib compatibility.
    """

    pass


class ZoneSchemaError(EzraError, ValueError):
    """Zone schema contract violation.

    Raised when zone schemas are invalid, duplicate, or violate registry constraints.
    Dual-inherits from ValueError to preserve stdlib compatibility.
    """

    pass


class DeterminismError(EzraError, RuntimeError):
    """Determinism verification failure.

    Raised when determinism checks fail (e.g., non-deterministic outputs).
    Dual-inherits from RuntimeError to preserve stdlib compatibility.
    """

    pass
