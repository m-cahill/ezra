"""Comprehensive contract tests for zone schema invariants.

This module tests the mandatory invariants (I1-I4) for the Universal Zone
Mapping Schema (UZMS):

I1 — Deterministic Zone Serialization: Identical zone definitions must
     produce byte-identical JSON.

I2 — Stable Zone Ordering: Zone list ordering must be stable and explicit
     (sorted by channel_index, id).

I3 — Plugin Isolation: ML plugins must not modify zone id, bbox coordinates,
     channel index, or persistence flags.

I4 — Schema Version Stability: Schema version must be declared and immutable
     unless explicitly bumped.
"""

from __future__ import annotations

import hashlib
import json

import pytest

from ezra.zones.registry import ZoneRegistry
from ezra.zones.schema import BBoxNorm, ZonePersistence, ZoneSchema
from ezra.zones.serialize import (
    SCHEMA_VERSION,
    serialize_zone_registry,
    validate_zone_data_against_schema,
)

# ============================================================================
# I1 — Deterministic Zone Serialization
# ============================================================================


def test_i1_byte_identical_serialization():
    """I1: Identical zone definitions must produce byte-identical JSON."""
    registry1 = ZoneRegistry()
    registry2 = ZoneRegistry()

    # Create identical zones in both registries
    bbox = BBoxNorm(x_min=0.1, y_min=0.2, x_max=0.9, y_max=0.8)
    persistence = ZonePersistence(sticky=True)

    zone1 = ZoneSchema(
        id="test_zone",
        kind="ocr",
        channel_index=0,
        bbox_norm=bbox,
        persistence=persistence,
    )

    zone2 = ZoneSchema(
        id="test_zone",
        kind="ocr",
        channel_index=0,
        bbox_norm=bbox,
        persistence=persistence,
    )

    registry1.register(zone1)
    registry2.register(zone2)
    registry1.freeze()
    registry2.freeze()

    # Serialize both registries
    json1 = serialize_zone_registry(registry1)
    json2 = serialize_zone_registry(registry2)

    # Must be byte-identical
    assert json1 == json2
    assert json1.encode("utf-8") == json2.encode("utf-8")

    # Hash comparison
    hash1 = hashlib.sha256(json1.encode("utf-8")).hexdigest()
    hash2 = hashlib.sha256(json2.encode("utf-8")).hexdigest()
    assert hash1 == hash2


def test_i1_multiple_runs_stable():
    """I1: Serialization must be stable across multiple calls."""
    registry = ZoneRegistry()

    bbox = BBoxNorm(x_min=0.123456, y_min=0.234567, x_max=0.789012, y_max=0.890123)
    persistence = ZonePersistence(sticky=True)

    zone = ZoneSchema(
        id="precision_zone",
        kind="segmentation",
        channel_index=2,
        bbox_norm=bbox,
        persistence=persistence,
    )

    registry.register(zone)
    registry.freeze()

    # Serialize multiple times
    json1 = serialize_zone_registry(registry)
    json2 = serialize_zone_registry(registry)
    json3 = serialize_zone_registry(registry)

    # All must be byte-identical
    assert json1 == json2 == json3

    # Hash comparison
    hashes = [hashlib.sha256(j.encode("utf-8")).hexdigest() for j in [json1, json2, json3]]
    assert len(set(hashes)) == 1  # All hashes identical


# ============================================================================
# I2 — Stable Zone Ordering
# ============================================================================


def test_i2_stable_ordering_by_channel_then_id():
    """I2: Zone list ordering must be stable (sorted by channel_index, id)."""
    registry = ZoneRegistry()

    bbox = BBoxNorm(x_min=0.0, y_min=0.0, x_max=1.0, y_max=1.0)
    persistence = ZonePersistence(sticky=True)

    # Register zones in non-sorted order
    # Registry enforces unique channel indices, so we test ordering by channel_index
    # (id ordering within same channel_index would require duplicate channels, which is not allowed)
    zone2 = ZoneSchema(
        id="zone_b", kind="ocr", channel_index=2, bbox_norm=bbox, persistence=persistence
    )
    zone0 = ZoneSchema(
        id="zone_a", kind="ocr", channel_index=0, bbox_norm=bbox, persistence=persistence
    )
    zone1 = ZoneSchema(
        id="zone_c", kind="ocr", channel_index=1, bbox_norm=bbox, persistence=persistence
    )

    # Register in non-sorted order
    registry.register(zone2)
    registry.register(zone0)
    registry.register(zone1)
    registry.freeze()

    # Export and verify order
    exported = registry.export_to_dict()
    zones = exported["zones"]

    # Must be sorted by (channel_index, id)
    # Since channel indices are unique, primary sort is by channel_index
    assert zones[0]["channel_index"] == 0
    assert zones[0]["id"] == "zone_a"
    assert zones[1]["channel_index"] == 1
    assert zones[1]["id"] == "zone_c"
    assert zones[2]["channel_index"] == 2
    assert zones[2]["id"] == "zone_b"


def test_i2_ordering_stable_across_exports():
    """I2: Ordering must be stable across multiple exports."""
    registry = ZoneRegistry()

    bbox = BBoxNorm(x_min=0.0, y_min=0.0, x_max=1.0, y_max=1.0)
    persistence = ZonePersistence(sticky=True)

    # Register zones
    for i in range(5):
        zone = ZoneSchema(
            id=f"zone_{i}",
            kind="ocr",
            channel_index=i,
            bbox_norm=bbox,
            persistence=persistence,
        )
        registry.register(zone)

    registry.freeze()

    # Export multiple times
    export1 = registry.export_to_dict()
    export2 = registry.export_to_dict()
    export3 = registry.export_to_dict()

    # Ordering must be identical
    ids1 = [z["id"] for z in export1["zones"]]
    ids2 = [z["id"] for z in export2["zones"]]
    ids3 = [z["id"] for z in export3["zones"]]

    assert ids1 == ids2 == ids3


# ============================================================================
# I3 — Plugin Isolation
# ============================================================================


def test_i3_zone_schema_immutable():
    """I3: ZoneSchema is frozen and cannot be mutated."""
    bbox = BBoxNorm(x_min=0.1, y_min=0.2, x_max=0.9, y_max=0.8)
    persistence = ZonePersistence(sticky=True)

    zone = ZoneSchema(
        id="test_zone",
        kind="ocr",
        channel_index=0,
        bbox_norm=bbox,
        persistence=persistence,
    )

    # Attempting to mutate should raise FrozenInstanceError
    with pytest.raises(Exception):  # FrozenInstanceError from dataclass
        zone.id = "mutated_id"  # type: ignore[misc]

    with pytest.raises(Exception):
        zone.channel_index = 999  # type: ignore[misc]

    with pytest.raises(Exception):
        zone.bbox_norm = BBoxNorm(x_min=0.0, y_min=0.0, x_max=1.0, y_max=1.0)  # type: ignore[misc]

    with pytest.raises(Exception):
        zone.persistence = ZonePersistence(sticky=False)  # type: ignore[misc]


def test_i3_bbox_norm_immutable():
    """I3: BBoxNorm is frozen and cannot be mutated."""
    bbox = BBoxNorm(x_min=0.1, y_min=0.2, x_max=0.9, y_max=0.8)

    # Attempting to mutate should raise FrozenInstanceError
    with pytest.raises(Exception):  # FrozenInstanceError from dataclass
        bbox.x_min = 0.0  # type: ignore[misc]

    with pytest.raises(Exception):
        bbox.y_max = 1.0  # type: ignore[misc]


def test_i3_persistence_immutable():
    """I3: ZonePersistence is frozen and cannot be mutated."""
    persistence = ZonePersistence(sticky=True)

    # Attempting to mutate should raise FrozenInstanceError
    with pytest.raises(Exception):  # FrozenInstanceError from dataclass
        persistence.sticky = False  # type: ignore[misc]


def test_i3_registry_frozen_prevents_mutation():
    """I3: Frozen registry prevents new registrations."""
    registry = ZoneRegistry()

    bbox = BBoxNorm(x_min=0.0, y_min=0.0, x_max=1.0, y_max=1.0)
    persistence = ZonePersistence(sticky=True)

    zone1 = ZoneSchema(
        id="zone1", kind="ocr", channel_index=0, bbox_norm=bbox, persistence=persistence
    )
    zone2 = ZoneSchema(
        id="zone2", kind="ocr", channel_index=1, bbox_norm=bbox, persistence=persistence
    )

    registry.register(zone1)
    registry.freeze()

    # Attempting to register after freeze should raise ZoneSchemaError
    from ezra.errors import ZoneSchemaError

    with pytest.raises(ZoneSchemaError, match="registry is frozen"):
        registry.register(zone2)


# ============================================================================
# I4 — Schema Version Stability
# ============================================================================


def test_i4_schema_version_constant():
    """I4: Schema version must be declared and constant."""
    # Version must be a string
    assert isinstance(SCHEMA_VERSION, str)

    # Version must be non-empty
    assert len(SCHEMA_VERSION) > 0

    # Version must match expected format (semver-like)
    assert SCHEMA_VERSION == "1.0.0"

    # Version must be immutable (constant, not variable)
    # This is enforced by Python's constant semantics, but we verify the value
    from ezra.zones.serialize import SCHEMA_VERSION as VERSION_IMPORT

    assert SCHEMA_VERSION == VERSION_IMPORT


def test_i4_schema_version_in_schema_file():
    """I4: Schema version should be referenced in schema_v1.json metadata."""
    import importlib.resources

    # Load schema file
    schema_text = (
        importlib.resources.files("ezra.zones")
        .joinpath("schema_v1.json")
        .read_text(encoding="utf-8")
    )
    schema = json.loads(schema_text)

    # Schema title should reference version
    assert "v1.0.0" in schema.get("title", "")


# ============================================================================
# Additional Contract Tests
# ============================================================================


def test_zone_data_validates_against_schema():
    """Test that exported zone data validates against schema_v1.json."""
    registry = ZoneRegistry()

    bbox1 = BBoxNorm(x_min=0.0, y_min=0.0, x_max=0.5, y_max=0.5)
    bbox2 = BBoxNorm(x_min=0.5, y_min=0.5, x_max=1.0, y_max=1.0)
    persistence = ZonePersistence(sticky=True)

    zone1 = ZoneSchema(
        id="zone1", kind="ocr", channel_index=0, bbox_norm=bbox1, persistence=persistence
    )
    zone2 = ZoneSchema(
        id="zone2", kind="detection", channel_index=1, bbox_norm=bbox2, persistence=persistence
    )

    registry.register(zone1)
    registry.register(zone2)
    registry.freeze()

    # Export to dict
    data = registry.export_to_dict()

    # Validate against schema (should not raise)
    validate_zone_data_against_schema(data)


def test_zone_data_roundtrip():
    """Test that zone data can be serialized and deserialized correctly."""
    registry = ZoneRegistry()

    bbox = BBoxNorm(x_min=0.123456, y_min=0.234567, x_max=0.789012, y_max=0.890123)
    persistence = ZonePersistence(sticky=True)

    original = ZoneSchema(
        id="test_zone",
        kind="ocr",
        channel_index=0,
        bbox_norm=bbox,
        persistence=persistence,
    )

    registry.register(original)
    registry.freeze()

    # Serialize
    serialized = serialize_zone_registry(registry)
    data = json.loads(serialized)

    # Deserialize and reconstruct
    reconstructed_zones = []
    for zone_dict in data["zones"]:
        bbox_obj = BBoxNorm(
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
            bbox_norm=bbox_obj,
            persistence=persistence_obj,
        )
        reconstructed_zones.append(zone)

    # Should match original
    assert len(reconstructed_zones) == 1
    assert reconstructed_zones[0] == original
