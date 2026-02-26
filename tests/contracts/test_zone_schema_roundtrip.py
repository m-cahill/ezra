"""Round-trip tests for zone schema serialization.

Tests that zone schemas can be serialized and deserialized correctly.
"""

from ezra.zones.registry import ZoneRegistry
from ezra.zones.schema import BBoxNorm, ZonePersistence, ZoneSchema


def test_zone_schema_roundtrip():
    """Test that zone schema can be serialized and reconstructed."""
    # Create original schema
    bbox = BBoxNorm(x_min=0.1, y_min=0.2, x_max=0.9, y_max=0.8)
    persistence = ZonePersistence(sticky=True)
    original = ZoneSchema(
        id="test_zone",
        kind="ocr",
        channel_index=0,
        bbox_norm=bbox,
        persistence=persistence,
    )

    # Serialize to dict
    serialized = original.to_dict()

    # Reconstruct from dict
    reconstructed_bbox = BBoxNorm(
        x_min=serialized["bbox_norm"]["x_min"],
        y_min=serialized["bbox_norm"]["y_min"],
        x_max=serialized["bbox_norm"]["x_max"],
        y_max=serialized["bbox_norm"]["y_max"],
    )
    reconstructed_persistence = ZonePersistence(sticky=serialized["persistence"]["sticky"])
    reconstructed = ZoneSchema(
        id=serialized["id"],
        kind=serialized["kind"],
        channel_index=serialized["channel_index"],
        bbox_norm=reconstructed_bbox,
        persistence=reconstructed_persistence,
    )

    # Should be equal
    assert reconstructed == original
    assert reconstructed.id == original.id
    assert reconstructed.kind == original.kind
    assert reconstructed.channel_index == original.channel_index
    assert reconstructed.bbox_norm == original.bbox_norm
    assert reconstructed.persistence == original.persistence


def test_registry_roundtrip():
    """Test that registry can be exported and zones reconstructed."""
    # Create registry with multiple zones
    registry = ZoneRegistry()
    bbox1 = BBoxNorm(x_min=0.0, y_min=0.0, x_max=0.5, y_max=0.5)
    bbox2 = BBoxNorm(x_min=0.5, y_min=0.5, x_max=1.0, y_max=1.0)
    persistence = ZonePersistence(sticky=True)

    schema1 = ZoneSchema(
        id="zone1",
        kind="ocr",
        channel_index=0,
        bbox_norm=bbox1,
        persistence=persistence,
    )
    schema2 = ZoneSchema(
        id="zone2",
        kind="detection",
        channel_index=1,
        bbox_norm=bbox2,
        persistence=persistence,
    )

    registry.register(schema1)
    registry.register(schema2)
    registry.freeze()

    # Export to dict
    exported = registry.export_to_dict()

    # Verify structure
    assert "zones" in exported
    assert len(exported["zones"]) == 2

    # Reconstruct zones from exported data
    reconstructed_zones = []
    for zone_dict in exported["zones"]:
        bbox = BBoxNorm(
            x_min=zone_dict["bbox_norm"]["x_min"],
            y_min=zone_dict["bbox_norm"]["y_min"],
            x_max=zone_dict["bbox_norm"]["x_max"],
            y_max=zone_dict["bbox_norm"]["y_max"],
        )
        persistence_obj = ZonePersistence(sticky=zone_dict["persistence"]["sticky"])
        zone = ZoneSchema(
            id=zone_dict["id"],
            kind=zone_dict["kind"],
            channel_index=zone_dict["channel_index"],
            bbox_norm=bbox,
            persistence=persistence_obj,
        )
        reconstructed_zones.append(zone)

    # Verify reconstructed zones match originals
    assert reconstructed_zones[0] == schema1
    assert reconstructed_zones[1] == schema2
