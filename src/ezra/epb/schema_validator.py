"""JSON Schema validation for EPB v1.0.0 bundles.

This module validates EPB bundle components against their JSON Schemas
before hash computation and file writing. Validation failures raise
EPBValidationError with human-readable error messages.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Any, cast

import jsonschema  # type: ignore[import-untyped]
from jsonschema import ValidationError

from ezra.errors import EPBValidationError

# Resolve schema directory relative to this file
# schema_validator.py is at: src/ezra/epb/schema_validator.py
# Schemas are at: docs/specs/epb_v1/schemas/
# Path: __file__ -> parents[3] -> docs/specs/epb_v1/schemas/
SCHEMA_DIR = Path(__file__).resolve().parents[3] / "docs" / "specs" / "epb_v1" / "schemas"

# Schema file names
MANIFEST_SCHEMA = "manifest.schema.json"
DETECTIONS_SCHEMA = "detections.schema.json"
STATE_SCHEMA = "state.schema.json"
DELTA_SCHEMA = "delta.schema.json"
HASHES_SCHEMA = "hashes.schema.json"

# In-memory schema cache (loaded once, reused)
_SCHEMA_CACHE: dict[str, dict[str, Any]] = {}


def _load_schema(schema_name: str) -> dict[str, Any]:
    """Load JSON Schema from file and cache it.

    Args:
        schema_name: Name of schema file (e.g., "manifest.schema.json").

    Returns:
        Parsed JSON Schema dictionary.

    Raises:
        FileNotFoundError: If schema file does not exist.
        json.JSONDecodeError: If schema file is invalid JSON.
        ValueError: If schema directory cannot be resolved.
    """
    if schema_name in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[schema_name]

    schema_path = SCHEMA_DIR / schema_name
    if not schema_path.exists():
        raise EPBValidationError(
            f"EPB schema file not found: {schema_path}. Expected schema directory: {SCHEMA_DIR}"
        )

    schema_content = schema_path.read_text(encoding="utf-8")
    schema_dict = cast(dict[str, Any], json.loads(schema_content))

    # Cache for future use
    _SCHEMA_CACHE[schema_name] = schema_dict
    return schema_dict


def _convert_mapping_to_dict(obj: Any) -> Any:
    """Recursively convert MappingProxyType to dict for JSON Schema validation.

    JSON Schema validators expect plain dict types, not MappingProxyType.
    This function converts MappingProxyType instances to dict while preserving
    the structure.

    Args:
        obj: Object to convert (dict, MappingProxyType, list, or primitive).

    Returns:
        Converted object with MappingProxyType replaced by dict.
    """
    if isinstance(obj, MappingProxyType):
        # Convert MappingProxyType to dict
        return {k: _convert_mapping_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, Mapping):
        # Handle other Mapping types (shouldn't happen, but be safe)
        return {k: _convert_mapping_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        # Preserve array order
        return [_convert_mapping_to_dict(item) for item in obj]
    else:
        # Primitive types pass through unchanged
        return obj


def _validate_against_schema(
    instance: dict[str, Any] | MappingProxyType, schema_name: str, component_name: str
) -> None:
    """Validate instance against a JSON Schema.

    Args:
        instance: Dictionary to validate (may be MappingProxyType).
        schema_name: Name of schema file (e.g., "manifest.schema.json").
        component_name: Human-readable name for error messages (e.g., "manifest").

    Raises:
        EPBValidationError: If validation fails, with detailed error message.
    """
    # Convert MappingProxyType to dict for JSON Schema validation
    # (jsonschema doesn't recognize MappingProxyType as a valid dict type)
    instance_dict = _convert_mapping_to_dict(instance)

    try:
        schema = _load_schema(schema_name)
        jsonschema.validate(instance=instance_dict, schema=schema)
    except ValidationError as e:
        # Format validation error for human readability
        error_path = ".".join(str(p) for p in e.absolute_path) if e.absolute_path else "root"
        error_msg = (
            f"EPB {component_name} validation failed: {e.message}\n"
            f"  Path: {error_path}\n"
            f"  Schema: {schema_name}"
        )
        raise EPBValidationError(error_msg) from e
    except FileNotFoundError as e:
        raise EPBValidationError(
            f"EPB schema file not found: {schema_name}. Cannot validate {component_name}."
        ) from e
    except json.JSONDecodeError as e:
        raise EPBValidationError(
            f"EPB schema file {schema_name} is invalid JSON. Cannot validate {component_name}."
        ) from e


def validate_bundle(bundle: dict[str, Any]) -> None:
    """Validate EPB bundle against JSON Schemas.

    Validates all bundle components:
    - manifest.json (required)
    - detections.json (required)
    - state.json (required)
    - delta.json (optional, only if present)
    - hashes.json (not validated here, validated after writing)

    Args:
        bundle: EPB bundle dictionary from build_epb_bundle().

    Raises:
        EPBValidationError: If any component fails validation, with detailed error message.
        KeyError: If required bundle components are missing.
    """
    # Validate manifest.json
    if "manifest" not in bundle:
        raise EPBValidationError("EPB bundle missing required 'manifest' component")
    _validate_against_schema(bundle["manifest"], MANIFEST_SCHEMA, "manifest")

    # Validate detections.json
    if "detections" not in bundle:
        raise EPBValidationError("EPB bundle missing required 'detections' component")
    _validate_against_schema(bundle["detections"], DETECTIONS_SCHEMA, "detections")

    # Validate state.json (always present per builder contract)
    if "state" not in bundle:
        raise EPBValidationError("EPB bundle missing required 'state' component")
    _validate_against_schema(bundle["state"], STATE_SCHEMA, "state")

    # Validate delta.json (optional, only if present)
    if bundle.get("delta") is not None:
        _validate_against_schema(bundle["delta"], DELTA_SCHEMA, "delta")
