"""Tests for zone schema registry."""

import pytest

from ezra.zones.registry import ZoneRegistry
from ezra.zones.schema import BBoxNorm, ZonePersistence, ZoneSchema


def test_registry_starts_empty():
    """Test registry starts empty."""
    registry = ZoneRegistry()
    assert registry.count == 0
    assert not registry.is_frozen
    assert registry.list_all() == []


def test_registry_register():
    """Test registering a zone schema."""
    registry = ZoneRegistry()
    bbox = BBoxNorm(x_min=0.0, y_min=0.0, x_max=1.0, y_max=1.0)
    persistence = ZonePersistence(sticky=True)
    schema = ZoneSchema(
        id="zone1",
        kind="ocr",
        channel_index=0,
        bbox_norm=bbox,
        persistence=persistence,
    )
    registry.register(schema)
    assert registry.count == 1
    assert registry.get("zone1") == schema


def test_registry_duplicate_id():
    """Test registering duplicate ID fails."""
    registry = ZoneRegistry()
    bbox = BBoxNorm(x_min=0.0, y_min=0.0, x_max=1.0, y_max=1.0)
    persistence = ZonePersistence(sticky=True)
    schema1 = ZoneSchema(
        id="zone1",
        kind="ocr",
        channel_index=0,
        bbox_norm=bbox,
        persistence=persistence,
    )
    schema2 = ZoneSchema(
        id="zone1",  # Duplicate!
        kind="detection",
        channel_index=1,
        bbox_norm=bbox,
        persistence=persistence,
    )
    registry.register(schema1)
    with pytest.raises(ValueError, match="Duplicate zone id"):
        registry.register(schema2)


def test_registry_duplicate_channel():
    """Test registering duplicate channel index fails."""
    registry = ZoneRegistry()
    bbox = BBoxNorm(x_min=0.0, y_min=0.0, x_max=1.0, y_max=1.0)
    persistence = ZonePersistence(sticky=True)
    schema1 = ZoneSchema(
        id="zone1",
        kind="ocr",
        channel_index=0,
        bbox_norm=bbox,
        persistence=persistence,
    )
    schema2 = ZoneSchema(
        id="zone2",
        kind="detection",
        channel_index=0,  # Duplicate!
        bbox_norm=bbox,
        persistence=persistence,
    )
    registry.register(schema1)
    with pytest.raises(ValueError, match="Duplicate channel index"):
        registry.register(schema2)


def test_registry_freeze():
    """Test freezing registry."""
    registry = ZoneRegistry()
    bbox = BBoxNorm(x_min=0.0, y_min=0.0, x_max=1.0, y_max=1.0)
    persistence = ZonePersistence(sticky=True)
    schema = ZoneSchema(
        id="zone1",
        kind="ocr",
        channel_index=0,
        bbox_norm=bbox,
        persistence=persistence,
    )
    registry.register(schema)
    registry.freeze()
    assert registry.is_frozen

    # Cannot register after freeze
    schema2 = ZoneSchema(
        id="zone2",
        kind="detection",
        channel_index=1,
        bbox_norm=bbox,
        persistence=persistence,
    )
    with pytest.raises(ValueError, match="registry is frozen"):
        registry.register(schema2)


def test_registry_list_all_sorted():
    """Test list_all returns zones sorted by (channel_index, id)."""
    registry = ZoneRegistry()
    bbox = BBoxNorm(x_min=0.0, y_min=0.0, x_max=1.0, y_max=1.0)
    persistence = ZonePersistence(sticky=True)

    # Register in non-sorted order
    schema2 = ZoneSchema(
        id="zone2",
        kind="ocr",
        channel_index=2,
        bbox_norm=bbox,
        persistence=persistence,
    )
    schema0 = ZoneSchema(
        id="zone0",
        kind="ocr",
        channel_index=0,
        bbox_norm=bbox,
        persistence=persistence,
    )
    schema1 = ZoneSchema(
        id="zone1",
        kind="ocr",
        channel_index=1,
        bbox_norm=bbox,
        persistence=persistence,
    )

    registry.register(schema2)
    registry.register(schema0)
    registry.register(schema1)

    all_zones = registry.list_all()
    assert [z.id for z in all_zones] == ["zone0", "zone1", "zone2"]
    assert [z.channel_index for z in all_zones] == [0, 1, 2]


def test_registry_export_to_dict():
    """Test export_to_dict produces deterministic output."""
    registry = ZoneRegistry()
    bbox = BBoxNorm(x_min=0.1, y_min=0.2, x_max=0.9, y_max=0.8)
    persistence = ZonePersistence(sticky=True)
    schema = ZoneSchema(
        id="zone1",
        kind="ocr",
        channel_index=0,
        bbox_norm=bbox,
        persistence=persistence,
    )
    registry.register(schema)

    result = registry.export_to_dict()
    assert "zones" in result
    assert len(result["zones"]) == 1
    assert result["zones"][0]["id"] == "zone1"
    assert result["zones"][0]["channel_index"] == 0
    assert result["zones"][0]["bbox_norm"]["x_min"] == 0.1


def test_registry_get_nonexistent():
    """Test get returns None for nonexistent zone."""
    registry = ZoneRegistry()
    assert registry.get("nonexistent") is None

