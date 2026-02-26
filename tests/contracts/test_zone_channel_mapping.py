"""Channel mapping contract tests.

Tests that channel indices are unique and properly validated.
"""

import pytest

from ezra.zones.registry import ZoneRegistry
from ezra.zones.schema import BBoxNorm, ZonePersistence, ZoneSchema


def test_channel_indices_unique():
    """Test that channel indices must be unique across registry."""
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


def test_channel_indices_non_negative():
    """Test that channel indices must be non-negative."""
    registry = ZoneRegistry()
    bbox = BBoxNorm(x_min=0.0, y_min=0.0, x_max=1.0, y_max=1.0)
    persistence = ZonePersistence(sticky=True)

    schema = ZoneSchema(
        id="zone1",
        kind="ocr",
        channel_index=-1,  # Invalid!
        bbox_norm=bbox,
        persistence=persistence,
    )

    with pytest.raises(ValueError, match="Channel index must be a non-negative integer"):
        registry.register(schema)


def test_channel_indices_can_be_non_contiguous():
    """Test that channel indices do not need to be contiguous."""
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
        channel_index=5,  # Non-contiguous, but valid
        bbox_norm=bbox,
        persistence=persistence,
    )
    schema3 = ZoneSchema(
        id="zone3",
        kind="segmentation",
        channel_index=10,  # Non-contiguous, but valid
        bbox_norm=bbox,
        persistence=persistence,
    )

    registry.register(schema1)
    registry.register(schema2)
    registry.register(schema3)
    registry.freeze()

    # Should succeed
    assert registry.count == 3
    zones = registry.list_all()
    assert [z.channel_index for z in zones] == [0, 5, 10]


def test_channel_mapping_export_order():
    """Test that exported zones are sorted by channel_index."""
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
    registry.freeze()

    # Export and verify order
    exported = registry.export_to_dict()
    channel_indices = [z["channel_index"] for z in exported["zones"]]
    assert channel_indices == [0, 1, 2]
