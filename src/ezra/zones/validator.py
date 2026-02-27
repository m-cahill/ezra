"""Zone schema validation rules.

This module provides validation for zone schemas, ensuring:
- Unique channel indices across registry
- Valid normalized bbox ranges (0 <= x_min < x_max <= 1, etc.)
- Unique zone IDs
- Non-empty strings for id and kind
- Non-negative channel indices
"""

from __future__ import annotations

from ezra.errors import ZoneSchemaError
from ezra.zones.schema import BBoxNorm, ZoneSchema


def validate_bbox(bbox: BBoxNorm) -> None:
    """Validate normalized bounding box.

    Args:
        bbox: Bounding box to validate.

    Raises:
        ZoneSchemaError: If bbox is invalid.
    """
    if not (0 <= bbox.x_min < bbox.x_max <= 1):
        raise ZoneSchemaError(
            f"Invalid bbox x coordinates: x_min={bbox.x_min}, x_max={bbox.x_max}. "
            "Must satisfy 0 <= x_min < x_max <= 1"
        )
    if not (0 <= bbox.y_min < bbox.y_max <= 1):
        raise ZoneSchemaError(
            f"Invalid bbox y coordinates: y_min={bbox.y_min}, y_max={bbox.y_max}. "
            "Must satisfy 0 <= y_min < y_max <= 1"
        )


def validate_zone_schema(schema: ZoneSchema) -> None:
    """Validate a single zone schema.

    Args:
        schema: Zone schema to validate.

    Raises:
        ZoneSchemaError: If schema is invalid.
    """
    # Validate id is non-empty
    if not schema.id or not isinstance(schema.id, str):
        raise ZoneSchemaError(f"Zone id must be a non-empty string, got: {schema.id!r}")

    # Validate kind is non-empty
    if not schema.kind or not isinstance(schema.kind, str):
        raise ZoneSchemaError(f"Zone kind must be a non-empty string, got: {schema.kind!r}")

    # Validate channel_index is non-negative integer
    if not isinstance(schema.channel_index, int) or schema.channel_index < 0:
        raise ZoneSchemaError(
            f"Channel index must be a non-negative integer, got: {schema.channel_index!r}"
        )

    # Validate bbox
    validate_bbox(schema.bbox_norm)


def validate_registry(
    schemas: list[ZoneSchema],
    *,
    check_unique_ids: bool = True,
    check_unique_channels: bool = True,
) -> None:
    """Validate a collection of zone schemas (registry-level validation).

    Args:
        schemas: List of zone schemas to validate.
        check_unique_ids: If True, ensure all zone IDs are unique.
        check_unique_channels: If True, ensure all channel indices are unique.

    Raises:
        ZoneSchemaError: If validation fails.
    """
    # Validate each schema individually
    for schema in schemas:
        validate_zone_schema(schema)

    # Check for duplicate IDs
    if check_unique_ids:
        seen_ids: set[str] = set()
        for schema in schemas:
            if schema.id in seen_ids:
                raise ZoneSchemaError(f"Duplicate zone id: {schema.id}")
            seen_ids.add(schema.id)

    # Check for duplicate channel indices
    if check_unique_channels:
        seen_channels: set[int] = set()
        for schema in schemas:
            if schema.channel_index in seen_channels:
                duplicate_ids = [s.id for s in schemas if s.channel_index == schema.channel_index]
                raise ZoneSchemaError(
                    f"Duplicate channel index: {schema.channel_index} "
                    f"(used by zones: {duplicate_ids})"
                )
            seen_channels.add(schema.channel_index)
