"""Integrity tests for zone registry runtime state.

Tests that verify registry integrity invariants:
- Freeze-state enforcement
- Channel uniqueness
- Registration ordering determinism
- Post-freeze immutability
"""

import pytest

from ezra.errors import ZoneSchemaError
from ezra.zones.registry import ZoneRegistry
from ezra.zones.schema import BBoxNorm, ZonePersistence, ZoneSchema
from ezra.zones.serialize import registry_hash


def test_freeze_enforcement_prevents_registration():
    """Test that freeze prevents new registrations."""
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
    registry.register(schema1)
    registry.freeze()

    # Verify frozen
    assert registry.is_frozen

    # Attempt to register after freeze should fail
    schema2 = ZoneSchema(
        id="zone2",
        kind="detection",
        channel_index=1,
        bbox_norm=bbox,
        persistence=persistence,
    )
    with pytest.raises(ZoneSchemaError, match="registry is frozen"):
        registry.register(schema2)


def test_freeze_state_is_terminal():
    """Test that freeze is idempotent and terminal."""
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

    # First freeze
    registry.freeze()
    assert registry.is_frozen
    hash_after_first_freeze = registry_hash(registry)

    # Second freeze (should be no-op)
    registry.freeze()
    assert registry.is_frozen
    hash_after_second_freeze = registry_hash(registry)

    # Hash should be unchanged
    assert hash_after_first_freeze == hash_after_second_freeze


def test_channel_uniqueness_enforced():
    """Test that channel indices must be unique."""
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
    registry.register(schema1)

    # Attempt to register with duplicate channel index
    schema2 = ZoneSchema(
        id="zone2",
        kind="detection",
        channel_index=0,  # Duplicate!
        bbox_norm=bbox,
        persistence=persistence,
    )
    with pytest.raises(ZoneSchemaError, match="Duplicate channel index"):
        registry.register(schema2)


def test_registration_ordering_determinism():
    """Test that zone ordering is deterministic regardless of insertion order."""
    # Create registry 1: insert in order 0, 1, 2
    registry1 = ZoneRegistry()
    bbox = BBoxNorm(x_min=0.0, y_min=0.0, x_max=1.0, y_max=1.0)
    persistence = ZonePersistence(sticky=True)

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
    schema2 = ZoneSchema(
        id="zone2",
        kind="ocr",
        channel_index=2,
        bbox_norm=bbox,
        persistence=persistence,
    )

    registry1.register(schema0)
    registry1.register(schema1)
    registry1.register(schema2)
    registry1.freeze()

    # Create registry 2: insert in reverse order 2, 1, 0
    registry2 = ZoneRegistry()
    registry2.register(schema2)
    registry2.register(schema1)
    registry2.register(schema0)
    registry2.freeze()

    # Both should produce identical ordering
    zones1 = registry1.list_all()
    zones2 = registry2.list_all()

    assert [z.id for z in zones1] == [z.id for z in zones2]
    assert [z.channel_index for z in zones1] == [z.channel_index for z in zones2]

    # Hashes should match
    hash1 = registry_hash(registry1)
    hash2 = registry_hash(registry2)
    assert hash1 == hash2, "Registry hash must be independent of insertion order"


def test_registry_hash_unchanged_after_failed_registration():
    """Test that registry hash is unchanged after failed registration attempt."""
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
    registry.register(schema1)
    registry.freeze()

    hash_before = registry_hash(registry)

    # Attempt invalid registration (should fail)
    schema2 = ZoneSchema(
        id="zone2",
        kind="detection",
        channel_index=1,
        bbox_norm=bbox,
        persistence=persistence,
    )
    with pytest.raises(ZoneSchemaError, match="registry is frozen"):
        registry.register(schema2)

    # Hash should be unchanged
    hash_after = registry_hash(registry)
    assert hash_before == hash_after


def test_channel_index_ordering_preserved():
    """Test that zones are ordered by (channel_index, id) regardless of insertion order."""
    registry = ZoneRegistry()
    bbox = BBoxNorm(x_min=0.0, y_min=0.0, x_max=1.0, y_max=1.0)
    persistence = ZonePersistence(sticky=True)

    # Insert zones with different channel indices and IDs
    # to verify sorting by (channel_index, id)
    schema_b = ZoneSchema(
        id="zone_b",
        kind="ocr",
        channel_index=2,
        bbox_norm=bbox,
        persistence=persistence,
    )
    schema_a = ZoneSchema(
        id="zone_a",
        kind="ocr",
        channel_index=1,
        bbox_norm=bbox,
        persistence=persistence,
    )
    schema_c = ZoneSchema(
        id="zone_c",
        kind="ocr",
        channel_index=0,
        bbox_norm=bbox,
        persistence=persistence,
    )

    # Insert out of order
    registry.register(schema_b)  # channel 2, id "b"
    registry.register(schema_a)  # channel 1, id "a"
    registry.register(schema_c)  # channel 0, id "c"

    registry.freeze()

    # Should be sorted by (channel_index, id)
    zones = registry.list_all()
    assert [z.id for z in zones] == ["zone_c", "zone_a", "zone_b"]
    assert [z.channel_index for z in zones] == [0, 1, 2]
