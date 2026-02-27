"""Snapshot tests for zone registry state.

Tests that zone registry state serialization is deterministic and matches
committed snapshot baseline. This validates runtime registry integrity,
not schema structure (which is covered by test_zone_schema_snapshot.py).
"""

import json
from pathlib import Path

from ezra.zones.registry import ZoneRegistry
from ezra.zones.schema import BBoxNorm, ZonePersistence, ZoneSchema
from ezra.zones.serialize import canonical_registry_json, registry_hash


def _create_snapshot_fixture_registry() -> ZoneRegistry:
    """Create a deterministic test registry for snapshot baseline.

    This fixture deliberately registers zones out of order to verify
    that ordering is stable regardless of insertion order.

    Returns:
        Frozen registry with 5 zones registered in non-sequential order.
    """
    registry = ZoneRegistry()

    # Register zones in deliberately out-of-order sequence
    # to verify ordering stability (should sort by channel_index, then id)

    # Zone 3 (channel 2)
    bbox3 = BBoxNorm(x_min=0.2, y_min=0.2, x_max=0.8, y_max=0.8)
    persistence3 = ZonePersistence(sticky=True)
    schema3 = ZoneSchema(
        id="zone_c",
        kind="ocr",
        channel_index=2,
        bbox_norm=bbox3,
        persistence=persistence3,
    )
    registry.register(schema3)

    # Zone 1 (channel 0)
    bbox1 = BBoxNorm(x_min=0.0, y_min=0.0, x_max=0.5, y_max=0.5)
    persistence1 = ZonePersistence(sticky=True)
    schema1 = ZoneSchema(
        id="zone_a",
        kind="ocr",
        channel_index=0,
        bbox_norm=bbox1,
        persistence=persistence1,
    )
    registry.register(schema1)

    # Zone 5 (channel 4)
    bbox5 = BBoxNorm(x_min=0.1, y_min=0.1, x_max=0.9, y_max=0.9)
    persistence5 = ZonePersistence(sticky=False)
    schema5 = ZoneSchema(
        id="zone_e",
        kind="detection",
        channel_index=4,
        bbox_norm=bbox5,
        persistence=persistence5,
    )
    registry.register(schema5)

    # Zone 2 (channel 1)
    bbox2 = BBoxNorm(x_min=0.5, y_min=0.5, x_max=1.0, y_max=1.0)
    persistence2 = ZonePersistence(sticky=False)
    schema2 = ZoneSchema(
        id="zone_b",
        kind="detection",
        channel_index=1,
        bbox_norm=bbox2,
        persistence=persistence2,
    )
    registry.register(schema2)

    # Zone 4 (channel 3)
    bbox4 = BBoxNorm(x_min=0.123456, y_min=0.234567, x_max=0.789012, y_max=0.890123)
    persistence4 = ZonePersistence(sticky=True)
    schema4 = ZoneSchema(
        id="zone_d",
        kind="segmentation",
        channel_index=3,
        bbox_norm=bbox4,
        persistence=persistence4,
    )
    registry.register(schema4)

    # Freeze registry
    registry.freeze()

    return registry


def test_registry_snapshot_matches():
    """Test that registry state snapshot matches committed baseline."""
    snapshot_path = Path(__file__).parent.parent / "docs" / "baselines" / "zone_registry_snapshot.json"
    registry = _create_snapshot_fixture_registry()

    # Generate canonical JSON
    canonical_json = canonical_registry_json(registry)

    # Load snapshot baseline
    if snapshot_path.exists():
        snapshot_json = snapshot_path.read_text(encoding="utf-8").strip()
        # Parse both to compare data structures (baseline is pretty-printed, canonical is compact)
        canonical_data = json.loads(canonical_json)
        snapshot_data = json.loads(snapshot_json)
        # Compare data structures (order-insensitive on parse, but structure should match)
        assert canonical_data == snapshot_data, (
            "Registry snapshot mismatch. "
            "If this is an intentional change, update the baseline."
        )
    else:
        # First run: write snapshot baseline
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        # Use pretty-printed format for baseline (easier to review)
        from ezra.zones.serialize import serialize_zone_registry_pretty
        pretty_json = serialize_zone_registry_pretty(registry)
        snapshot_path.write_text(pretty_json, encoding="utf-8", newline="")
        # Verify canonical matches
        snapshot_json = snapshot_path.read_text(encoding="utf-8").strip()
        snapshot_data = json.loads(snapshot_json)
        canonical_data = json.loads(canonical_json)
        assert canonical_data == snapshot_data


def test_registry_hash_determinism():
    """Test that registry hash is deterministic across multiple calls."""
    registry1 = _create_snapshot_fixture_registry()
    registry2 = _create_snapshot_fixture_registry()

    # Compute hashes
    hash1 = registry_hash(registry1)
    hash2 = registry_hash(registry2)

    # Should be identical
    assert hash1 == hash2, "Registry hash must be deterministic"

    # Hash should be 64-character hex string (SHA256)
    assert len(hash1) == 64
    assert all(c in "0123456789abcdef" for c in hash1)


def test_registry_hash_stability():
    """Test that registry hash remains stable after freeze."""
    registry = _create_snapshot_fixture_registry()

    # Hash before freeze (should already be frozen by fixture)
    hash_after_freeze = registry_hash(registry)

    # Create identical registry and verify hash matches
    registry2 = _create_snapshot_fixture_registry()
    hash_after_freeze2 = registry_hash(registry2)

    assert hash_after_freeze == hash_after_freeze2

    # Verify hash is stable across multiple calls on same registry
    hash_call1 = registry_hash(registry)
    hash_call2 = registry_hash(registry)
    assert hash_call1 == hash_call2


def test_registry_canonical_json_determinism():
    """Test that canonical JSON is byte-identical across multiple calls."""
    registry = _create_snapshot_fixture_registry()

    # Generate canonical JSON multiple times
    json1 = canonical_registry_json(registry)
    json2 = canonical_registry_json(registry)

    # Should be byte-identical
    assert json1 == json2, "Canonical JSON must be byte-identical"

    # Verify it's valid JSON
    data = json.loads(json1)
    assert "zones" in data
    assert isinstance(data["zones"], list)

