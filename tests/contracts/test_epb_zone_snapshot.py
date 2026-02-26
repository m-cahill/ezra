"""Snapshot tests for EPB bundles with zones.

Tests that EPB bundle emission with zones is deterministic and matches committed snapshots.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from ezra.epb import build_epb_bundle, write_epb_bundle
from ezra.zones import BBoxNorm, ZonePersistence, ZoneRegistry, ZoneSchema

# Fixed timestamp for determinism
FIXED_TIMESTAMP = datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)


def _create_test_registry() -> ZoneRegistry:
    """Create a deterministic test registry with sample zones."""
    registry = ZoneRegistry()

    # Zone 1: OCR zone
    zone1 = ZoneSchema(
        id="ocr_zone",
        kind="ocr",
        channel_index=0,
        bbox_norm=BBoxNorm(x_min=0.0, y_min=0.0, x_max=0.5, y_max=0.5),
        persistence=ZonePersistence(sticky=True),
    )

    # Zone 2: Detection zone
    zone2 = ZoneSchema(
        id="detection_zone",
        kind="detection",
        channel_index=1,
        bbox_norm=BBoxNorm(x_min=0.5, y_min=0.5, x_max=1.0, y_max=1.0),
        persistence=ZonePersistence(sticky=False),
    )

    registry.register(zone1)
    registry.register(zone2)
    registry.freeze()

    return registry


def test_epb_baseline_snapshot(tmp_path: Path) -> None:
    """Test that EPB bundle without zones matches baseline structure."""
    bundle = build_epb_bundle(
        detections=[{"text": "Hello", "confidence": 0.9, "bbox": [10.0, 20.0, 50.0, 40.0]}],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 200, "height": 100, "channels": 3},
        timestamp=FIXED_TIMESTAMP,
    )

    output_dir = tmp_path / "epb_baseline"
    write_epb_bundle(bundle, output_dir)

    # Verify zones.json is not present (baseline)
    assert not (output_dir / "zones.json").exists()

    # Verify hashes.json structure (no zones.json entry)
    hashes_content = (output_dir / "hashes.json").read_text(encoding="utf-8")
    hashes = json.loads(hashes_content)
    assert "zones.json" not in hashes["files"]

    # Verify required files exist
    assert (output_dir / "manifest.json").exists()
    assert (output_dir / "detections.json").exists()
    assert (output_dir / "state.json").exists()
    assert (output_dir / "hashes.json").exists()


def test_epb_zones_snapshot_matches(tmp_path: Path) -> None:
    """Test that EPB bundle with zones matches committed snapshot."""
    bundle = build_epb_bundle(
        detections=[{"text": "Hello", "confidence": 0.9, "bbox": [10.0, 20.0, 50.0, 40.0]}],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 200, "height": 100, "channels": 3},
        timestamp=FIXED_TIMESTAMP,
    )

    registry = _create_test_registry()
    output_dir = tmp_path / "epb_zones"
    write_epb_bundle(bundle, output_dir, zone_registry=registry)

    # Read zones.json
    zones_path = output_dir / "zones.json"
    assert zones_path.exists()
    zones_content = zones_path.read_text(encoding="utf-8")
    zones_data = json.loads(zones_content)

    # Snapshot path
    snapshot_path = Path(__file__).parent / "snapshots" / "epb_zones_snapshot.json"

    if snapshot_path.exists():
        # Compare with committed snapshot
        snapshot_data = json.loads(snapshot_path.read_text(encoding="utf-8"))
        assert zones_data == snapshot_data
    else:
        # First run: write snapshot
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        json_str = json.dumps(zones_data, sort_keys=True, indent=2)
        snapshot_path.write_text(json_str + "\n", encoding="utf-8", newline="")
        # Re-read to verify
        snapshot_data = json.loads(snapshot_path.read_text(encoding="utf-8"))
        assert zones_data == snapshot_data


def test_epb_zones_hashes_snapshot(tmp_path: Path) -> None:
    """Test that hashes.json structure with zones matches expected format."""
    bundle = build_epb_bundle(
        detections=[{"text": "Hello", "confidence": 0.9, "bbox": [10.0, 20.0, 50.0, 40.0]}],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 200, "height": 100, "channels": 3},
        timestamp=FIXED_TIMESTAMP,
    )

    registry = _create_test_registry()
    output_dir = tmp_path / "epb_zones"
    write_epb_bundle(bundle, output_dir, zone_registry=registry)

    # Read hashes.json
    hashes_content = (output_dir / "hashes.json").read_text(encoding="utf-8")
    hashes = json.loads(hashes_content)

    # Verify structure
    assert hashes["epb_version"] == "1.0.0"
    assert "bundle_hash" in hashes
    assert "files" in hashes

    # Verify zones.json is in files map
    assert "zones.json" in hashes["files"]
    zones_hash = hashes["files"]["zones.json"]
    assert len(zones_hash) == 64  # SHA256 hex string

    # Verify all required files present
    required_files = ["manifest.json", "detections.json", "state.json", "zones.json", "hashes.json"]
    for filename in required_files:
        assert filename in hashes["files"]


def test_epb_zones_byte_stable(tmp_path: Path) -> None:
    """Test that EPB bundle with zones is byte-stable across multiple emissions."""
    bundle = build_epb_bundle(
        detections=[{"text": "Hello", "confidence": 0.9, "bbox": [10.0, 20.0, 50.0, 40.0]}],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 200, "height": 100, "channels": 3},
        timestamp=FIXED_TIMESTAMP,
    )

    registry = _create_test_registry()

    output_dir1 = tmp_path / "epb1"
    output_dir2 = tmp_path / "epb2"

    write_epb_bundle(bundle, output_dir1, zone_registry=registry)
    write_epb_bundle(bundle, output_dir2, zone_registry=registry)

    # Compare zones.json (should be byte-identical)
    zones1_content = (output_dir1 / "zones.json").read_text(encoding="utf-8")
    zones2_content = (output_dir2 / "zones.json").read_text(encoding="utf-8")
    assert zones1_content == zones2_content

    # Compare hashes.json (should be byte-identical)
    hashes1_content = (output_dir1 / "hashes.json").read_text(encoding="utf-8")
    hashes2_content = (output_dir2 / "hashes.json").read_text(encoding="utf-8")
    assert hashes1_content == hashes2_content

