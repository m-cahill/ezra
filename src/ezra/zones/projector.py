"""Zone-scoped state projection utility.

This module provides deterministic projection of perception outputs
(OCR detections) into zone-scoped partitions based on spatial containment.

Projection is a pure functional operation that assigns detections to zones
by checking if the detection's centroid falls within a zone's normalized
bounding box.
"""

from __future__ import annotations

import json
import math
from typing import Any

from ezra.errors import EPBCanonicalError, ZoneSchemaError
from ezra.types import OCRResult
from ezra.zones.registry import ZoneRegistry
from ezra.zones.schema import ZoneSchema

# Zone schema contract requires 6 decimal places for float precision
ZONE_FLOAT_PRECISION = 6


def project_state_to_zones(
    detections: list[OCRResult],
    registry: ZoneRegistry,
    image_width: int,
    image_height: int,
) -> dict[str, list[OCRResult]]:
    """Project detections into zone-scoped partitions.

    Each detection is assigned to zones whose normalized bounding box
    contains the detection's centroid (normalized to 0-1 space).

    Rules:
    - Registry must be frozen
    - Detection centroid computed in pixel space, then normalized
    - If detection matches multiple zones → ValueError (strict mode)
    - If detection matches no zone → silently dropped
    - Zones sorted by zone_id for deterministic ordering
    - Detection order preserved within each zone
    - Original detections not mutated

    Args:
        detections: List of OCR detection results (bbox in pixel coordinates).
        registry: Zone registry (must be frozen).
        image_width: Image width in pixels (for normalization).
        image_height: Image height in pixels (for normalization).

    Returns:
        Dictionary mapping zone_id to list of OCRResult objects assigned to that zone.
        Zones are sorted by zone_id. Detections within each zone preserve original order.

    Raises:
        ZoneSchemaError: If registry is not frozen, or image dimensions are invalid.
        ZoneSchemaError: If a detection matches multiple zones (strict mode violation).
    """
    if not registry.is_frozen:
        raise ZoneSchemaError("ZoneRegistry must be frozen before projection")

    if image_width <= 0 or image_height <= 0:
        raise ZoneSchemaError(
            f"Image dimensions must be positive, got width={image_width}, height={image_height}"
        )

    # Get all zones sorted by zone_id for deterministic ordering
    zones = sorted(registry.list_all(), key=lambda z: z.id)

    # Initialize result dict (will be sorted by zone_id due to sorted zones)
    result: dict[str, list[OCRResult]] = {}

    # Process each detection
    for detection in detections:
        # Extract bbox in pixel coordinates [x1, y1, x2, y2]
        if len(detection.bbox) != 4:
            # Skip invalid bbox (not our responsibility to validate)
            continue

        x1, y1, x2, y2 = detection.bbox

        # Compute centroid in pixel space
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0

        # Normalize to 0-1 space
        nx = cx / image_width
        ny = cy / image_height

        # Find zones that contain this normalized centroid
        matching_zones: list[ZoneSchema] = []
        for zone in zones:
            bbox = zone.bbox_norm
            # Check if centroid is within zone bbox (inclusive x_min/y_min, exclusive x_max/y_max)
            if bbox.x_min <= nx < bbox.x_max and bbox.y_min <= ny < bbox.y_max:
                matching_zones.append(zone)

        # Strict mode: error if multiple zones match
        if len(matching_zones) > 1:
            zone_ids = [z.id for z in matching_zones]
            raise ZoneSchemaError(
                f"Detection overlaps multiple zones: {zone_ids}. "
                "Strict mode requires unique zone assignment."
            )

        # If exactly one zone matches, assign detection to that zone
        if len(matching_zones) == 1:
            zone_id = matching_zones[0].id
            if zone_id not in result:
                result[zone_id] = []
            result[zone_id].append(detection)

        # If no zone matches, silently drop (no error, no special key)

    return result


def _canonicalize_projection_value(obj: Any) -> Any:
    """Recursively canonicalize a value for projection JSON serialization.

    Uses 6 decimal place precision (zone contract) instead of EPB's 8dp.

    Args:
        obj: Value to canonicalize (dict, list, float, or primitive).

    Returns:
        Canonicalized value.

    Raises:
        EPBCanonicalError: If object contains NaN or Infinity values.
    """
    if isinstance(obj, dict):
        # Sort keys alphabetically (case-sensitive) for determinism
        return {k: _canonicalize_projection_value(v) for k, v in sorted(obj.items())}
    elif isinstance(obj, list):
        # Preserve array order (arrays are ordered structures)
        return [_canonicalize_projection_value(item) for item in obj]
    elif isinstance(obj, float):
        # Reject NaN and Infinity
        if math.isnan(obj):
            raise EPBCanonicalError("NaN values are not permitted in projection output")
        if math.isinf(obj):
            raise EPBCanonicalError("Infinity values are not permitted in projection output")
        # Round to 6 decimal places (zone contract precision)
        return round(obj, ZONE_FLOAT_PRECISION)
    else:
        # Primitive types (str, int, bool, None) pass through unchanged
        return obj


def _ocr_result_to_dict(detection: OCRResult) -> dict[str, Any]:
    """Convert OCRResult to dictionary for JSON serialization.

    Args:
        detection: OCR detection result.

    Returns:
        Dictionary with keys: ["text", "confidence", "bbox", "metadata"]
        Floats rounded to 6dp precision.
    """
    result: dict[str, Any] = {
        "text": detection.text,
        "confidence": round(detection.confidence, ZONE_FLOAT_PRECISION),
        "bbox": [round(coord, ZONE_FLOAT_PRECISION) for coord in detection.bbox],
    }
    if detection.metadata is not None:
        result["metadata"] = detection.metadata
    return result


def to_projection_canonical_json(
    projection: dict[str, list[OCRResult]],
) -> str:
    """Convert projection result to canonical JSON string.

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
    - Zones sorted by zone_id
    - Detections within each zone preserve original order

    Args:
        projection: Dictionary mapping zone_id to list of OCRResult objects.

    Returns:
        Canonical JSON string with sorted keys and 6dp rounded floats.

    Raises:
        EPBCanonicalError: If projection contains NaN or Infinity values.
    """
    # Convert projection to JSON-serializable dict
    # Sort zones by zone_id for deterministic ordering
    serializable: dict[str, Any] = {}
    for zone_id in sorted(projection.keys()):
        detections = projection[zone_id]
        serializable[zone_id] = [_ocr_result_to_dict(det) for det in detections]

    # Canonicalize the object (round floats to 6dp, sort dict keys)
    canonicalized = _canonicalize_projection_value(serializable)

    # Serialize with zone contract rules:
    # - indent=2 (human-readable)
    # - sort_keys=True (already sorted by _canonicalize_projection_value, but explicit)
    # - ensure_ascii=False (UTF-8)
    # - allow_nan=False (reject NaN/Infinity)
    return json.dumps(
        canonicalized,
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    )
