"""Canonical serialization utilities for zone schemas.

This module provides byte-level canonicalization and version management
for zone schema serialization. It handles deterministic JSON encoding
with explicit precision control and stable key ordering.

The export.py module delegates to this module for canonical serialization
and handles file I/O concerns separately.
"""

from __future__ import annotations

import json
from typing import Any

from ezra.zones.registry import ZoneRegistry

# Schema version constant - immutable unless explicitly bumped in a milestone
SCHEMA_VERSION = "1.0.0"


def serialize_zone_registry(registry: ZoneRegistry) -> str:
    """Serialize zone registry to canonical JSON string.

    Args:
        registry: Zone registry to serialize.

    Returns:
        Canonical JSON string with:
        - Sorted keys at all levels
        - 6 decimal place float precision (via registry.export_to_dict())
        - No trailing whitespace
        - LF line endings (implicit in string)
        - Deterministic zone ordering (sorted by channel_index, id)

    Note:
        This function produces byte-identical output for identical registries.
        The registry.export_to_dict() method already handles deterministic
        ordering and float precision. This function adds canonical JSON
        formatting (sorted keys, no whitespace variability).
    """
    data = registry.export_to_dict()

    # Canonical JSON: sort_keys=True, no indent (compact), no trailing whitespace
    # This ensures byte-identical output for identical data
    json_str = json.dumps(data, sort_keys=True, separators=(",", ":"))

    return json_str


def serialize_zone_registry_pretty(registry: ZoneRegistry) -> str:
    """Serialize zone registry to pretty-printed JSON string.

    Args:
        registry: Zone registry to serialize.

    Returns:
        Pretty-printed JSON string with:
        - Sorted keys at all levels
        - 2-space indentation
        - Trailing newline
        - Deterministic zone ordering

    Note:
        This is for human-readable output. For byte-identical canonical
        form, use serialize_zone_registry() instead.
    """
    data = registry.export_to_dict()

    # Pretty-printed: sort_keys=True, indent=2, trailing newline
    json_str = json.dumps(data, sort_keys=True, indent=2)

    return json_str + "\n"


def validate_zone_data_against_schema(data: dict[str, Any]) -> None:
    """Validate zone data dictionary against schema_v1.json.

    Args:
        data: Zone data dictionary (from registry.export_to_dict()).

    Raises:
        jsonschema.ValidationError: If data does not conform to schema.
        FileNotFoundError: If schema file cannot be loaded.
        json.JSONDecodeError: If schema file is invalid JSON.

    Note:
        This function loads the schema from src/ezra/zones/schema_v1.json
        using importlib.resources for package-relative resolution.
    """
    import importlib.resources  # noqa: PLC0415

    import jsonschema  # type: ignore[import-untyped]

    # Load schema from package
    schema_text = importlib.resources.files("ezra.zones").joinpath("schema_v1.json").read_text(
        encoding="utf-8"
    )
    schema = json.loads(schema_text)

    # Validate data against schema
    jsonschema.validate(instance=data, schema=schema)

