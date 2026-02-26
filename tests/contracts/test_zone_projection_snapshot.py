"""Snapshot tests for zone projection.

Tests that zone projection is deterministic and matches committed snapshot.
"""

import json
from pathlib import Path

from ezra.types import OCRResult
from ezra.zones import (
    BBoxNorm,
    ZonePersistence,
    ZoneRegistry,
    ZoneSchema,
    project_state_to_zones,
    to_projection_canonical_json,
)


def _create_test_registry() -> ZoneRegistry:
    """Create a deterministic test registry with sample zones."""
    registry = ZoneRegistry()

    # Zone 1: OCR zone (left half)
    zone1 = ZoneSchema(
        id="ocr_zone",
        kind="ocr",
        channel_index=0,
        bbox_norm=BBoxNorm(x_min=0.0, y_min=0.0, x_max=0.5, y_max=0.5),
        persistence=ZonePersistence(sticky=True),
    )

    # Zone 2: Detection zone (right half)
    zone2 = ZoneSchema(
        id="detection_zone",
        kind="detection",
        channel_index=1,
        bbox_norm=BBoxNorm(x_min=0.5, y_min=0.5, x_max=1.0, y_max=1.0),
        persistence=ZonePersistence(sticky=False),
    )

    registry.register(zone1)
    registry.register(zone2)
    registry.freeze()

    return registry


def test_zone_projection_snapshot_matches():
    """Test that zone projection matches committed snapshot."""
    registry = _create_test_registry()

    # Fixed detections
    detections = [
        OCRResult(
            text="Hello",
            confidence=0.9123456789,
            bbox=[40.0, 40.0, 60.0, 60.0],  # Centroid at (50, 50) in 200x200 = (0.25, 0.25) -> ocr_zone
        ),
        OCRResult(
            text="World",
            confidence=0.8567890123,
            bbox=[140.0, 140.0, 160.0, 160.0],  # Centroid at (150, 150) in 200x200 = (0.75, 0.75) -> detection_zone
        ),
    ]

    # Project detections
    projection = project_state_to_zones(detections, registry, image_width=200, image_height=200)

    # Serialize to canonical JSON
    json_str = to_projection_canonical_json(projection)

    # Load expected snapshot
    snapshot_path = Path(__file__).parent / "snapshots" / "zone_projection_snapshot.json"
    expected_json = snapshot_path.read_text(encoding="utf-8").rstrip()

    # Compare JSON strings (should be identical, ignoring trailing whitespace)
    assert json_str == expected_json, (
        f"Projection JSON does not match snapshot.\n"
        f"Expected:\n{expected_json}\n\n"
        f"Got:\n{json_str}"
    )


def test_zone_projection_snapshot_roundtrip():
    """Test that snapshot can be parsed and matches projection structure."""
    registry = _create_test_registry()

    detections = [
        OCRResult(text="Hello", confidence=0.9123456789, bbox=[40.0, 40.0, 60.0, 60.0]),
        OCRResult(text="World", confidence=0.8567890123, bbox=[140.0, 140.0, 160.0, 160.0]),
    ]

    projection = project_state_to_zones(detections, registry, image_width=200, image_height=200)
    json_str = to_projection_canonical_json(projection)

    # Load snapshot
    snapshot_path = Path(__file__).parent / "snapshots" / "zone_projection_snapshot.json"
    snapshot_json = snapshot_path.read_text(encoding="utf-8")

    # Parse both
    parsed_projection = json.loads(json_str)
    parsed_snapshot = json.loads(snapshot_json)

    # Compare structure
    assert parsed_projection == parsed_snapshot

