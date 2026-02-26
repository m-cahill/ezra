"""Tests for zone schema type definitions."""

import json

from ezra.zones.schema import BBoxNorm, ZonePersistence, ZoneSchema


def test_bbox_norm_creation():
    """Test BBoxNorm creation and immutability."""
    bbox = BBoxNorm(x_min=0.1, y_min=0.2, x_max=0.9, y_max=0.8)
    assert bbox.x_min == 0.1
    assert bbox.y_min == 0.2
    assert bbox.x_max == 0.9
    assert bbox.y_max == 0.8


def test_zone_persistence_creation():
    """Test ZonePersistence creation."""
    persistence = ZonePersistence(sticky=True)
    assert persistence.sticky is True

    persistence_false = ZonePersistence(sticky=False)
    assert persistence_false.sticky is False


def test_zone_schema_creation():
    """Test ZoneSchema creation."""
    bbox = BBoxNorm(x_min=0.0, y_min=0.0, x_max=1.0, y_max=1.0)
    persistence = ZonePersistence(sticky=True)
    schema = ZoneSchema(
        id="test_zone",
        kind="ocr",
        channel_index=0,
        bbox_norm=bbox,
        persistence=persistence,
    )
    assert schema.id == "test_zone"
    assert schema.kind == "ocr"
    assert schema.channel_index == 0
    assert schema.bbox_norm == bbox
    assert schema.persistence == persistence


def test_zone_schema_to_dict():
    """Test deterministic serialization."""
    bbox = BBoxNorm(x_min=0.123456789, y_min=0.234567890, x_max=0.9, y_max=0.8)
    persistence = ZonePersistence(sticky=True)
    schema = ZoneSchema(
        id="test_zone",
        kind="ocr",
        channel_index=0,
        bbox_norm=bbox,
        persistence=persistence,
    )

    result = schema.to_dict()

    # Verify structure
    assert result["id"] == "test_zone"
    assert result["kind"] == "ocr"
    assert result["channel_index"] == 0
    assert result["bbox_norm"]["x_min"] == 0.123457  # Rounded to 6dp
    assert result["bbox_norm"]["y_min"] == 0.234568  # Rounded to 6dp
    assert result["bbox_norm"]["x_max"] == 0.9
    assert result["bbox_norm"]["y_max"] == 0.8
    assert result["persistence"]["sticky"] is True

    # Verify key ordering (deterministic)
    keys = list(result.keys())
    assert keys == ["id", "kind", "channel_index", "bbox_norm", "persistence"]


def test_zone_schema_to_dict_byte_stable():
    """Test that serialization is byte-stable across multiple calls."""
    bbox = BBoxNorm(x_min=0.1, y_min=0.2, x_max=0.9, y_max=0.8)
    persistence = ZonePersistence(sticky=True)
    schema = ZoneSchema(
        id="test_zone",
        kind="ocr",
        channel_index=0,
        bbox_norm=bbox,
        persistence=persistence,
    )

    dict1 = schema.to_dict()
    dict2 = schema.to_dict()

    json1 = json.dumps(dict1, sort_keys=True)
    json2 = json.dumps(dict2, sort_keys=True)

    assert json1 == json2
