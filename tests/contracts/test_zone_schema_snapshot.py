"""Snapshot tests for zone schema serialization.

Tests that zone schema serialization is deterministic and matches committed snapshot.
"""

import json
from pathlib import Path

from ezra.zones.registry import ZoneRegistry
from ezra.zones.schema import BBoxNorm, ZonePersistence, ZoneSchema


def _create_test_registry() -> ZoneRegistry:
    """Create a deterministic test registry with sample zones."""
    registry = ZoneRegistry()

    # Zone 1: OCR zone
    bbox1 = BBoxNorm(x_min=0.0, y_min=0.0, x_max=0.5, y_max=0.5)
    persistence1 = ZonePersistence(sticky=True)
    schema1 = ZoneSchema(
        id="ocr_zone",
        kind="ocr",
        channel_index=0,
        bbox_norm=bbox1,
        persistence=persistence1,
    )

    # Zone 2: Detection zone
    bbox2 = BBoxNorm(x_min=0.5, y_min=0.5, x_max=1.0, y_max=1.0)
    persistence2 = ZonePersistence(sticky=False)
    schema2 = ZoneSchema(
        id="detection_zone",
        kind="detection",
        channel_index=1,
        bbox_norm=bbox2,
        persistence=persistence2,
    )

    # Zone 3: Another zone with non-integer bbox coordinates
    bbox3 = BBoxNorm(x_min=0.123456, y_min=0.234567, x_max=0.789012, y_max=0.890123)
    persistence3 = ZonePersistence(sticky=True)
    schema3 = ZoneSchema(
        id="precision_zone",
        kind="segmentation",
        channel_index=2,
        bbox_norm=bbox3,
        persistence=persistence3,
    )

    registry.register(schema1)
    registry.register(schema2)
    registry.register(schema3)
    registry.freeze()

    return registry


def test_zone_schema_snapshot_matches():
    """Test that zone schema export matches committed snapshot."""
    snapshot_path = Path(__file__).parent / "snapshots" / "zone_schema_snapshot.json"
    registry = _create_test_registry()

    # Export to dict
    exported = registry.export_to_dict()

    # Load snapshot
    if snapshot_path.exists():
        snapshot_data = json.loads(snapshot_path.read_text(encoding="utf-8"))
        # Compare (order-insensitive on parse, but structure should match)
        assert exported == snapshot_data
    else:
        # First run: write snapshot
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        json_str = json.dumps(exported, sort_keys=True, indent=2)
        snapshot_path.write_text(json_str + "\n", encoding="utf-8", newline="")
        # Re-read to verify
        snapshot_data = json.loads(snapshot_path.read_text(encoding="utf-8"))
        assert exported == snapshot_data


def test_zone_schema_byte_stable():
    """Test that serialization is byte-stable across multiple exports."""
    registry = _create_test_registry()

    # Export twice
    dict1 = registry.export_to_dict()
    dict2 = registry.export_to_dict()

    # Serialize to JSON strings
    json1 = json.dumps(dict1, sort_keys=True, indent=2)
    json2 = json.dumps(dict2, sort_keys=True, indent=2)

    # Should be byte-identical
    assert json1 == json2

    # Also test individual zone serialization
    zones = registry.list_all()
    for zone in zones:
        dict1 = zone.to_dict()
        dict2 = zone.to_dict()
        json1 = json.dumps(dict1, sort_keys=True)
        json2 = json.dumps(dict2, sort_keys=True)
        assert json1 == json2

