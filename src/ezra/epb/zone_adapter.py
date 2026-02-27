"""Zone registry adapter for EPB bundle emission.

This module provides an adapter layer that converts ZoneRegistry
to a canonical dictionary suitable for inclusion in EPB bundles.

The adapter preserves zone schema contract precision (6 decimal places)
and maintains deterministic serialization order.
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from typing import Any

from ezra.errors import EPBCanonicalError, ZoneSchemaError
from ezra.zones.registry import ZoneRegistry

# Zone schema contract requires 6 decimal places for float precision
ZONE_FLOAT_PRECISION = 6


def _canonicalize_zone_value(obj: Any) -> Any:
    """Recursively canonicalize a value for zone JSON serialization.

    Uses 6 decimal place precision (zone contract) instead of EPB's 8dp.

    Args:
        obj: Value to canonicalize (dict, MappingProxyType, list, float, or primitive).

    Returns:
        Canonicalized value.
    """
    if isinstance(obj, Mapping):
        # Handle dict and MappingProxyType (sealed dicts)
        # Sort keys alphabetically (case-sensitive) for determinism
        return {k: _canonicalize_zone_value(v) for k, v in sorted(obj.items())}
    elif isinstance(obj, list):
        # Preserve array order (arrays are ordered structures)
        return [_canonicalize_zone_value(item) for item in obj]
    elif isinstance(obj, float):
        # Reject NaN and Infinity
        if math.isnan(obj):
            raise EPBCanonicalError("NaN values are not permitted in zone schemas")
        if math.isinf(obj):
            raise EPBCanonicalError("Infinity values are not permitted in zone schemas")
        # Round to 6 decimal places (zone contract precision)
        return round(obj, ZONE_FLOAT_PRECISION)
    else:
        # Primitive types (str, int, bool, None) pass through unchanged
        return obj


def to_zone_canonical_json(obj: Any) -> str:
    """Convert object to canonical JSON string for zones.json.

    Uses zone schema contract precision (6 decimal places) instead of
    EPB's 8 decimal places. This preserves the zone contract determinism
    established in M12.

    Rules:
    - UTF-8 encoding (ensure_ascii=False)
    - LF line endings (indent=2 produces LF)
    - Sorted keys (alphabetical, case-sensitive)
    - 6 decimal place float precision (zone contract)
    - No NaN/Infinity (allow_nan=False)
    - Indented 2-space JSON (human-readable canonical form)

    Args:
        obj: Object to serialize (typically dict).

    Returns:
        Canonical JSON string with sorted keys and 6dp rounded floats.

    Raises:
        EPBCanonicalError: If object contains NaN or Infinity values.
    """
    # Canonicalize the object (round floats to 6dp, sort dict keys)
    canonicalized = _canonicalize_zone_value(obj)

    # Serialize with zone contract rules:
    # - indent=2 (human-readable)
    # - sort_keys=True (already sorted by _canonicalize_zone_value, but explicit)
    # - ensure_ascii=False (UTF-8)
    # - allow_nan=False (reject NaN/Infinity)
    return json.dumps(
        canonicalized,
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    )


def adapt_zone_registry_to_epb(registry: ZoneRegistry) -> dict[str, Any]:
    """Convert ZoneRegistry to canonical dictionary for EPB zones.json.

    The returned dictionary is deterministic and ready for JSON serialization.
    Zone schema contract precision (6 decimal places) is preserved.

    Args:
        registry: Zone registry to adapt (must be frozen).

    Returns:
        Dictionary with structure:
        {
            "zones": [
                {zone_schema_dict},
                ...
            ]
        }
        Zones are sorted by (channel_index, id) for determinism.

    Raises:
        ZoneSchemaError: If registry is not frozen.
    """
    if not registry.is_frozen:
        raise ZoneSchemaError("Zone registry must be frozen before EPB emission")

    # Export registry to dict (already deterministic, 6dp precision)
    return registry.export_to_dict()
