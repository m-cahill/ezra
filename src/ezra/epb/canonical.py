"""Canonical JSON serialization for EPB v1.0.0.

This module implements EPB v1.0.0 canonicalization rules:
- UTF-8 encoding
- LF line endings
- Sorted keys (alphabetical, case-sensitive)
- 8 decimal place float precision
- No NaN/Infinity values
- Indented 2-space JSON (human-readable canonical form)

Note: This is independent from baseline canonicalization (which uses 6dp).
Future harmonization may be considered, but M08 keeps them separate.
"""

from __future__ import annotations

import json
import math
from typing import Any

# EPB v1.0.0 requires 8 decimal places for float precision
EPB_FLOAT_PRECISION = 8


def canonicalize_float(value: float) -> float:
    """Round float to EPB v1.0.0 precision (8 decimal places).

    Rejects NaN and Infinity values per EPB spec.

    Args:
        value: Float value to canonicalize.

    Returns:
        Rounded float value.

    Raises:
        ValueError: If value is NaN or Infinity.
    """
    if math.isnan(value):
        raise ValueError("NaN values are not permitted in EPB bundles")
    if math.isinf(value):
        raise ValueError("Infinity values are not permitted in EPB bundles")

    return round(value, EPB_FLOAT_PRECISION)


def _canonicalize_value(obj: Any) -> Any:
    """Recursively canonicalize a value for EPB serialization.

    Args:
        obj: Value to canonicalize (dict, list, float, or primitive).

    Returns:
        Canonicalized value.
    """
    if isinstance(obj, dict):
        # Sort keys alphabetically (case-sensitive) per EPB spec
        return {k: _canonicalize_value(v) for k, v in sorted(obj.items())}
    elif isinstance(obj, list):
        # Preserve array order (arrays are ordered structures)
        return [_canonicalize_value(item) for item in obj]
    elif isinstance(obj, float):
        return canonicalize_float(obj)
    else:
        # Primitive types (str, int, bool, None) pass through unchanged
        return obj


def to_canonical_json(obj: Any) -> str:
    """Convert object to canonical JSON string per EPB v1.0.0 spec.

    Rules:
    - UTF-8 encoding (ensure_ascii=False)
    - LF line endings (indent=2 produces LF)
    - Sorted keys (alphabetical, case-sensitive)
    - 8 decimal place float precision
    - No NaN/Infinity (allow_nan=False)
    - Indented 2-space JSON (human-readable canonical form)

    Args:
        obj: Object to serialize (typically dict or list).

    Returns:
        Canonical JSON string with sorted keys and rounded floats.

    Raises:
        ValueError: If object contains NaN or Infinity values.
    """
    # Canonicalize the object (round floats, sort dict keys)
    canonicalized = _canonicalize_value(obj)

    # Serialize with EPB v1.0.0 rules:
    # - indent=2 (human-readable, spec Section 3.2)
    # - sort_keys=True (already sorted by _canonicalize_value, but explicit)
    # - ensure_ascii=False (UTF-8, spec Section 3.1)
    # - allow_nan=False (reject NaN/Infinity, spec Section 3.3)
    return json.dumps(
        canonicalized,
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    )
