"""Tests for zone schema type definitions."""

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

