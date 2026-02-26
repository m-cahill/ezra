"""Zone-scoped state projection utility.

This module provides deterministic projection of perception outputs
(OCR detections) into zone-scoped partitions based on spatial containment.

Projection is a pure functional operation that assigns detections to zones
by checking if the detection's centroid falls within a zone's normalized
bounding box.
"""

from __future__ import annotations

from ezra.types import OCRResult
from ezra.zones.registry import ZoneRegistry
from ezra.zones.schema import ZoneSchema


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
        ValueError: If registry is not frozen, or if a detection matches multiple zones.
    """
    if not registry.is_frozen:
        raise ValueError("ZoneRegistry must be frozen before projection")

    if image_width <= 0 or image_height <= 0:
        raise ValueError(
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
            if (
                bbox.x_min <= nx < bbox.x_max
                and bbox.y_min <= ny < bbox.y_max
            ):
                matching_zones.append(zone)

        # Strict mode: error if multiple zones match
        if len(matching_zones) > 1:
            zone_ids = [z.id for z in matching_zones]
            raise ValueError(
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

