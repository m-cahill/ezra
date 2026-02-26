"""Tests for zone-aware EPB bundle emission."""

import json
from pathlib import Path

import pytest

from ezra.epb import build_epb_bundle, write_epb_bundle
from ezra.zones import BBoxNorm, ZonePersistence, ZoneRegistry, ZoneSchema


def test_epb_without_zones_backward_compatible(tmp_path: Path) -> None:
    """Test that EPB without zones preserves legacy behavior."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    output_dir = tmp_path / "epb"
    write_epb_bundle(bundle, output_dir)

    # Verify zones.json is not present
    assert not (output_dir / "zones.json").exists()

    # Verify hashes.json does not include zones.json
    hashes_content = (output_dir / "hashes.json").read_text(encoding="utf-8")
    hashes = json.loads(hashes_content)
    assert "zones.json" not in hashes["files"]


def test_epb_with_empty_zones_registry(tmp_path: Path) -> None:
    """Test EPB emission with empty zones registry."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    registry = ZoneRegistry()
    registry.freeze()

    output_dir = tmp_path / "epb"
    write_epb_bundle(bundle, output_dir, zone_registry=registry)

    # Verify zones.json exists
    assert (output_dir / "zones.json").exists()

    # Verify zones.json structure
    zones_content = (output_dir / "zones.json").read_text(encoding="utf-8")
    zones = json.loads(zones_content)
    assert "zones" in zones
    assert zones["zones"] == []

    # Verify hashes.json includes zones.json
    hashes_content = (output_dir / "hashes.json").read_text(encoding="utf-8")
    hashes = json.loads(hashes_content)
    assert "zones.json" in hashes["files"]
    assert len(hashes["files"]["zones.json"]) == 64  # SHA256 hex string


def test_epb_with_populated_zones_registry(tmp_path: Path) -> None:
    """Test EPB emission with populated zones registry."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    registry = ZoneRegistry()
    zone1 = ZoneSchema(
        id="zone1",
        kind="text",
        channel_index=0,
        bbox_norm=BBoxNorm(x_min=0.1, y_min=0.2, x_max=0.5, y_max=0.6),
        persistence=ZonePersistence(sticky=True),
    )
    zone2 = ZoneSchema(
        id="zone2",
        kind="button",
        channel_index=1,
        bbox_norm=BBoxNorm(x_min=0.6, y_min=0.2, x_max=0.9, y_max=0.6),
        persistence=ZonePersistence(sticky=False),
    )
    registry.register(zone1)
    registry.register(zone2)
    registry.freeze()

    output_dir = tmp_path / "epb"
    write_epb_bundle(bundle, output_dir, zone_registry=registry)

    # Verify zones.json exists
    assert (output_dir / "zones.json").exists()

    # Verify zones.json structure and content
    zones_content = (output_dir / "zones.json").read_text(encoding="utf-8")
    zones = json.loads(zones_content)
    assert "zones" in zones
    assert len(zones["zones"]) == 2

    # Verify zones are sorted by (channel_index, id)
    assert zones["zones"][0]["id"] == "zone1"  # channel_index=0
    assert zones["zones"][1]["id"] == "zone2"  # channel_index=1

    # Verify zone schema fields
    zone1_dict = zones["zones"][0]
    assert zone1_dict["id"] == "zone1"
    assert zone1_dict["kind"] == "text"
    assert zone1_dict["channel_index"] == 0
    assert zone1_dict["bbox_norm"]["x_min"] == 0.1
    assert zone1_dict["persistence"]["sticky"] is True

    # Verify hashes.json includes zones.json
    hashes_content = (output_dir / "hashes.json").read_text(encoding="utf-8")
    hashes = json.loads(hashes_content)
    assert "zones.json" in hashes["files"]


def test_epb_zones_hash_included_in_bundle_hash(tmp_path: Path) -> None:
    """Test that zones.json hash is included in bundle_hash computation."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    registry = ZoneRegistry()
    zone = ZoneSchema(
        id="zone1",
        kind="text",
        channel_index=0,
        bbox_norm=BBoxNorm(x_min=0.1, y_min=0.2, x_max=0.5, y_max=0.6),
        persistence=ZonePersistence(sticky=True),
    )
    registry.register(zone)
    registry.freeze()

    output_dir = tmp_path / "epb"
    write_epb_bundle(bundle, output_dir, zone_registry=registry)

    # Read hashes.json
    hashes_content = (output_dir / "hashes.json").read_text(encoding="utf-8")
    hashes = json.loads(hashes_content)

    # Verify zones.json is in files map
    assert "zones.json" in hashes["files"]
    zones_hash = hashes["files"]["zones.json"]

    # Verify bundle_hash includes zones.json (by checking it's different from bundle without zones)
    bundle_with_zones_hash = hashes["bundle_hash"]

    # Create bundle without zones for comparison
    output_dir_no_zones = tmp_path / "epb_no_zones"
    write_epb_bundle(bundle, output_dir_no_zones)

    hashes_no_zones_content = (output_dir_no_zones / "hashes.json").read_text(encoding="utf-8")
    hashes_no_zones = json.loads(hashes_no_zones_content)
    bundle_no_zones_hash = hashes_no_zones["bundle_hash"]

    # Bundle hashes should differ (zones.json affects bundle_hash)
    assert bundle_with_zones_hash != bundle_no_zones_hash


def test_epb_zones_6dp_precision(tmp_path: Path) -> None:
    """Test that zones.json uses 6 decimal place precision (zone contract)."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    registry = ZoneRegistry()
    # Use float with more than 6 decimal places
    zone = ZoneSchema(
        id="zone1",
        kind="text",
        channel_index=0,
        bbox_norm=BBoxNorm(x_min=0.123456789, y_min=0.234567890, x_max=0.5, y_max=0.6),
        persistence=ZonePersistence(sticky=True),
    )
    registry.register(zone)
    registry.freeze()

    output_dir = tmp_path / "epb"
    write_epb_bundle(bundle, output_dir, zone_registry=registry)

    # Read zones.json
    zones_content = (output_dir / "zones.json").read_text(encoding="utf-8")
    zones = json.loads(zones_content)

    # Verify floats are rounded to 6 decimal places
    bbox = zones["zones"][0]["bbox_norm"]
    assert bbox["x_min"] == 0.123457  # Rounded to 6dp
    assert bbox["y_min"] == 0.234568  # Rounded to 6dp


def test_epb_zones_unfrozen_registry_raises_error(tmp_path: Path) -> None:
    """Test that unfrozen registry raises ValueError."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    registry = ZoneRegistry()
    # Registry not frozen

    output_dir = tmp_path / "epb"
    with pytest.raises(ValueError, match="must be frozen"):
        write_epb_bundle(bundle, output_dir, zone_registry=registry)


def test_epb_zones_deterministic(tmp_path: Path) -> None:
    """Test that zones.json emission is deterministic."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    registry = ZoneRegistry()
    zone = ZoneSchema(
        id="zone1",
        kind="text",
        channel_index=0,
        bbox_norm=BBoxNorm(x_min=0.1, y_min=0.2, x_max=0.5, y_max=0.6),
        persistence=ZonePersistence(sticky=True),
    )
    registry.register(zone)
    registry.freeze()

    output_dir1 = tmp_path / "epb1"
    output_dir2 = tmp_path / "epb2"

    write_epb_bundle(bundle, output_dir1, zone_registry=registry)
    write_epb_bundle(bundle, output_dir2, zone_registry=registry)

    # Compare zones.json (should be identical)
    zones1_content = (output_dir1 / "zones.json").read_text(encoding="utf-8")
    zones2_content = (output_dir2 / "zones.json").read_text(encoding="utf-8")
    assert zones1_content == zones2_content

    # Compare hashes.json (should be identical)
    hashes1_content = (output_dir1 / "hashes.json").read_text(encoding="utf-8")
    hashes2_content = (output_dir2 / "hashes.json").read_text(encoding="utf-8")
    assert hashes1_content == hashes2_content


def test_epb_zones_hash_verification(tmp_path: Path) -> None:
    """Test that zones.json hash verification works."""
    from ezra.epb import verify_epb_bundle

    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    registry = ZoneRegistry()
    zone = ZoneSchema(
        id="zone1",
        kind="text",
        channel_index=0,
        bbox_norm=BBoxNorm(x_min=0.1, y_min=0.2, x_max=0.5, y_max=0.6),
        persistence=ZonePersistence(sticky=True),
    )
    registry.register(zone)
    registry.freeze()

    output_dir = tmp_path / "epb"
    write_epb_bundle(bundle, output_dir, zone_registry=registry)

    # Verification should pass (called automatically, but test explicitly)
    verify_epb_bundle(output_dir)

    # Tamper zones.json
    zones_path = output_dir / "zones.json"
    zones_content = zones_path.read_text(encoding="utf-8")
    zones = json.loads(zones_content)
    zones["zones"][0]["id"] = "tampered"
    zones_path.write_text(json.dumps(zones, indent=2) + "\n", encoding="utf-8")

    # Verification should fail
    with pytest.raises(ValueError, match="zones.json hash mismatch"):
        verify_epb_bundle(output_dir)

