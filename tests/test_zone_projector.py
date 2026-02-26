"""Tests for zone-scoped state projection."""

import json

import pytest

from ezra.types import OCRResult
from ezra.zones import (
    BBoxNorm,
    ZonePersistence,
    ZoneRegistry,
    ZoneSchema,
    project_state_to_zones,
    to_projection_canonical_json,
)


def test_zone_projector_basic_assignment():
    """Test basic detection assignment to zones."""
    # Create registry with two zones
    registry = ZoneRegistry()
    zone1 = ZoneSchema(
        id="zone1",
        kind="text",
        channel_index=0,
        bbox_norm=BBoxNorm(x_min=0.0, y_min=0.0, x_max=0.5, y_max=0.5),
        persistence=ZonePersistence(sticky=True),
    )
    zone2 = ZoneSchema(
        id="zone2",
        kind="button",
        channel_index=1,
        bbox_norm=BBoxNorm(x_min=0.5, y_min=0.5, x_max=1.0, y_max=1.0),
        persistence=ZonePersistence(sticky=False),
    )
    registry.register(zone1)
    registry.register(zone2)
    registry.freeze()

    # Create detections
    # Detection 1: centroid at (0.25, 0.25) -> zone1
    # Detection 2: centroid at (0.75, 0.75) -> zone2
    detections = [
        OCRResult(
            text="Hello",
            confidence=0.9,
            bbox=[40.0, 40.0, 60.0, 60.0],  # Centroid at (50, 50) in 200x200 image = (0.25, 0.25)
        ),
        OCRResult(
            text="World",
            confidence=0.85,
            # Centroid at (150, 150) in 200x200 image = (0.75, 0.75)
            bbox=[140.0, 140.0, 160.0, 160.0],
        ),
    ]

    result = project_state_to_zones(detections, registry, image_width=200, image_height=200)

    assert len(result) == 2
    assert "zone1" in result
    assert "zone2" in result
    assert len(result["zone1"]) == 1
    assert len(result["zone2"]) == 1
    assert result["zone1"][0].text == "Hello"
    assert result["zone2"][0].text == "World"


def test_zone_projector_empty_registry():
    """Test projection with empty registry."""
    registry = ZoneRegistry()
    registry.freeze()

    detections = [
        OCRResult(text="Hello", confidence=0.9, bbox=[10.0, 20.0, 50.0, 40.0]),
    ]

    result = project_state_to_zones(detections, registry, image_width=200, image_height=200)

    assert result == {}


def test_zone_projector_overlapping_zone_error():
    """Test that detection matching multiple zones raises ValueError."""
    registry = ZoneRegistry()
    # Two overlapping zones
    zone1 = ZoneSchema(
        id="zone1",
        kind="text",
        channel_index=0,
        bbox_norm=BBoxNorm(x_min=0.0, y_min=0.0, x_max=0.6, y_max=0.6),
        persistence=ZonePersistence(sticky=True),
    )
    zone2 = ZoneSchema(
        id="zone2",
        kind="button",
        channel_index=1,
        bbox_norm=BBoxNorm(x_min=0.4, y_min=0.4, x_max=1.0, y_max=1.0),
        persistence=ZonePersistence(sticky=False),
    )
    registry.register(zone1)
    registry.register(zone2)
    registry.freeze()

    # Detection centroid at (0.5, 0.5) -> matches both zones
    detections = [
        OCRResult(
            text="Overlap",
            confidence=0.9,
            bbox=[90.0, 90.0, 110.0, 110.0],  # Centroid at (100, 100) in 200x200 image = (0.5, 0.5)
        ),
    ]

    with pytest.raises(ValueError, match="Detection overlaps multiple zones"):
        project_state_to_zones(detections, registry, image_width=200, image_height=200)


def test_zone_projector_deterministic_order():
    """Test that projection result has deterministic zone ordering."""
    registry = ZoneRegistry()
    # Register zones in non-alphabetical order
    zone_c = ZoneSchema(
        id="zone_c",
        kind="text",
        channel_index=2,
        bbox_norm=BBoxNorm(x_min=0.6, y_min=0.6, x_max=1.0, y_max=1.0),
        persistence=ZonePersistence(sticky=True),
    )
    zone_a = ZoneSchema(
        id="zone_a",
        kind="text",
        channel_index=0,
        bbox_norm=BBoxNorm(x_min=0.0, y_min=0.0, x_max=0.3, y_max=0.3),
        persistence=ZonePersistence(sticky=True),
    )
    zone_b = ZoneSchema(
        id="zone_b",
        kind="text",
        channel_index=1,
        bbox_norm=BBoxNorm(x_min=0.3, y_min=0.3, x_max=0.6, y_max=0.6),
        persistence=ZonePersistence(sticky=True),
    )
    registry.register(zone_c)
    registry.register(zone_a)
    registry.register(zone_b)
    registry.freeze()

    detections = [
        OCRResult(text="A", confidence=0.9, bbox=[10.0, 10.0, 50.0, 50.0]),  # zone_a
        OCRResult(text="B", confidence=0.85, bbox=[70.0, 70.0, 110.0, 110.0]),  # zone_b
        OCRResult(text="C", confidence=0.8, bbox=[130.0, 130.0, 170.0, 170.0]),  # zone_c
    ]

    result = project_state_to_zones(detections, registry, image_width=200, image_height=200)

    # Zones should be sorted by zone_id
    zone_ids = list(result.keys())
    assert zone_ids == ["zone_a", "zone_b", "zone_c"]

    # Detections within each zone should preserve original order
    assert result["zone_a"][0].text == "A"
    assert result["zone_b"][0].text == "B"
    assert result["zone_c"][0].text == "C"


def test_zone_projector_bbox_edge_precision():
    """Test bbox edge cases (inclusive min, exclusive max)."""
    registry = ZoneRegistry()
    zone = ZoneSchema(
        id="zone1",
        kind="text",
        channel_index=0,
        bbox_norm=BBoxNorm(x_min=0.0, y_min=0.0, x_max=0.5, y_max=0.5),
        persistence=ZonePersistence(sticky=True),
    )
    registry.register(zone)
    registry.freeze()

    # Centroid exactly at (0.0, 0.0) -> should match (inclusive min)
    det1 = OCRResult(text="Edge1", confidence=0.9, bbox=[0.0, 0.0, 10.0, 10.0])
    # Centroid exactly at (0.5, 0.5) -> should NOT match (exclusive max)
    det2 = OCRResult(text="Edge2", confidence=0.85, bbox=[90.0, 90.0, 110.0, 110.0])

    result = project_state_to_zones([det1, det2], registry, image_width=200, image_height=200)

    assert "zone1" in result
    assert len(result["zone1"]) == 1
    assert result["zone1"][0].text == "Edge1"


def test_zone_projector_unfrozen_registry_error():
    """Test that unfrozen registry raises ValueError."""
    registry = ZoneRegistry()
    zone = ZoneSchema(
        id="zone1",
        kind="text",
        channel_index=0,
        bbox_norm=BBoxNorm(x_min=0.0, y_min=0.0, x_max=1.0, y_max=1.0),
        persistence=ZonePersistence(sticky=True),
    )
    registry.register(zone)
    # Not frozen!

    detections = [
        OCRResult(text="Hello", confidence=0.9, bbox=[10.0, 20.0, 50.0, 40.0]),
    ]

    with pytest.raises(ValueError, match="ZoneRegistry must be frozen before projection"):
        project_state_to_zones(detections, registry, image_width=200, image_height=200)


def test_zone_projector_unassigned_detections_dropped():
    """Test that detections matching no zone are silently dropped."""
    registry = ZoneRegistry()
    zone = ZoneSchema(
        id="zone1",
        kind="text",
        channel_index=0,
        bbox_norm=BBoxNorm(x_min=0.0, y_min=0.0, x_max=0.3, y_max=0.3),
        persistence=ZonePersistence(sticky=True),
    )
    registry.register(zone)
    registry.freeze()

    detections = [
        OCRResult(text="InZone", confidence=0.9, bbox=[10.0, 10.0, 50.0, 50.0]),  # Matches zone1
        OCRResult(text="OutZone", confidence=0.85, bbox=[100.0, 100.0, 150.0, 150.0]),  # No match
    ]

    result = project_state_to_zones(detections, registry, image_width=200, image_height=200)

    assert "zone1" in result
    assert len(result["zone1"]) == 1
    assert result["zone1"][0].text == "InZone"
    # OutZone should be dropped (not in result)


def test_zone_projector_invalid_image_dimensions():
    """Test that invalid image dimensions raise ValueError."""
    registry = ZoneRegistry()
    registry.freeze()

    detections = [
        OCRResult(text="Hello", confidence=0.9, bbox=[10.0, 20.0, 50.0, 40.0]),
    ]

    with pytest.raises(ValueError, match="Image dimensions must be positive"):
        project_state_to_zones(detections, registry, image_width=0, image_height=200)

    with pytest.raises(ValueError, match="Image dimensions must be positive"):
        project_state_to_zones(detections, registry, image_width=200, image_height=-1)


def test_zone_projector_invalid_bbox_skipped():
    """Test that detections with invalid bbox are skipped."""
    registry = ZoneRegistry()
    zone = ZoneSchema(
        id="zone1",
        kind="text",
        channel_index=0,
        bbox_norm=BBoxNorm(x_min=0.0, y_min=0.0, x_max=1.0, y_max=1.0),
        persistence=ZonePersistence(sticky=True),
    )
    registry.register(zone)
    registry.freeze()

    detections = [
        OCRResult(text="Valid", confidence=0.9, bbox=[10.0, 20.0, 50.0, 40.0]),  # Valid
        OCRResult(text="Invalid", confidence=0.85, bbox=[10.0, 20.0]),  # Invalid (only 2 coords)
    ]

    result = project_state_to_zones(detections, registry, image_width=200, image_height=200)

    assert "zone1" in result
    assert len(result["zone1"]) == 1
    assert result["zone1"][0].text == "Valid"


def test_zone_projector_no_mutation():
    """Test that original detections are not mutated."""
    registry = ZoneRegistry()
    zone = ZoneSchema(
        id="zone1",
        kind="text",
        channel_index=0,
        bbox_norm=BBoxNorm(x_min=0.0, y_min=0.0, x_max=1.0, y_max=1.0),
        persistence=ZonePersistence(sticky=True),
    )
    registry.register(zone)
    registry.freeze()

    detections = [
        OCRResult(text="Hello", confidence=0.9, bbox=[10.0, 20.0, 50.0, 40.0]),
    ]

    original_bbox = detections[0].bbox.copy()
    result = project_state_to_zones(detections, registry, image_width=200, image_height=200)

    # Original detection unchanged
    assert detections[0].bbox == original_bbox
    # Result contains same detection object (reference equality)
    assert result["zone1"][0] is detections[0]


def test_to_projection_canonical_json_basic():
    """Test canonical JSON serialization of projection."""
    # Create a projection result
    det1 = OCRResult(
        text="Hello",
        confidence=0.9123456789,
        bbox=[10.123456789, 20.123456789, 50.123456789, 40.123456789],
    )
    det2 = OCRResult(
        text="World",
        confidence=0.8567890123,
        bbox=[60.123456789, 20.123456789, 100.123456789, 40.123456789],
    )

    projection = {
        "zone2": [det2],  # Intentionally non-sorted order
        "zone1": [det1],
    }

    json_str = to_projection_canonical_json(projection)

    # Should be valid JSON
    parsed = json.loads(json_str)

    # Zones should be sorted
    zone_ids = list(parsed.keys())
    assert zone_ids == ["zone1", "zone2"]

    # Floats should be rounded to 6dp
    assert parsed["zone1"][0]["confidence"] == 0.912346
    assert parsed["zone1"][0]["bbox"][0] == 10.123457


def test_to_projection_canonical_json_deterministic():
    """Test that canonical JSON is deterministic across multiple calls."""
    det = OCRResult(text="Test", confidence=0.9, bbox=[10.0, 20.0, 50.0, 40.0])
    projection = {"zone1": [det]}

    json1 = to_projection_canonical_json(projection)
    json2 = to_projection_canonical_json(projection)

    assert json1 == json2


def test_to_projection_canonical_json_empty_projection():
    """Test canonical JSON serialization of empty projection."""
    projection = {}
    json_str = to_projection_canonical_json(projection)

    parsed = json.loads(json_str)
    assert parsed == {}


def test_to_projection_canonical_json_multiple_detections_per_zone():
    """Test canonical JSON with multiple detections per zone."""
    det1 = OCRResult(text="First", confidence=0.9, bbox=[10.0, 20.0, 50.0, 40.0])
    det2 = OCRResult(text="Second", confidence=0.85, bbox=[60.0, 20.0, 100.0, 40.0])
    det3 = OCRResult(text="Third", confidence=0.8, bbox=[110.0, 20.0, 150.0, 40.0])

    projection = {
        "zone1": [det1, det2, det3],
    }

    json_str = to_projection_canonical_json(projection)
    parsed = json.loads(json_str)

    assert len(parsed["zone1"]) == 3
    assert parsed["zone1"][0]["text"] == "First"
    assert parsed["zone1"][1]["text"] == "Second"
    assert parsed["zone1"][2]["text"] == "Third"


def test_to_projection_canonical_json_metadata_preserved():
    """Test that metadata is preserved in canonical JSON."""
    det = OCRResult(
        text="Test",
        confidence=0.9,
        bbox=[10.0, 20.0, 50.0, 40.0],
        metadata={"key": "value", "number": 42},
    )
    projection = {"zone1": [det]}

    json_str = to_projection_canonical_json(projection)
    parsed = json.loads(json_str)

    assert parsed["zone1"][0]["metadata"] == {"key": "value", "number": 42}


def test_to_projection_canonical_json_no_metadata():
    """Test canonical JSON when detection has no metadata."""
    det = OCRResult(text="Test", confidence=0.9, bbox=[10.0, 20.0, 50.0, 40.0], metadata=None)
    projection = {"zone1": [det]}

    json_str = to_projection_canonical_json(projection)
    parsed = json.loads(json_str)

    assert "metadata" not in parsed["zone1"][0]
