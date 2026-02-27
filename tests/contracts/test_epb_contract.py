"""EPB bundle consumer contract harness.

Tests that EPB bundle output structure remains stable and deterministic.
This is the primary consumer contract surface for EZRA.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from ezra.epb import build_epb_bundle, write_epb_bundle


# Fixed timestamp for determinism
FIXED_TIMESTAMP = datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)


def _normalize_epb_bundle_for_snapshot(bundle_dir: Path) -> dict:
    """Normalize EPB bundle for snapshot comparison.

    Strips non-deterministic fields:
    - Timestamps (manifest.timestamp, state.timestamp) → "<TIMESTAMP>"
    - Platform-specific fields (manifest.platform → "<PLATFORM>", manifest.python_version → "<PYTHON_VERSION>")
    - EZRA version (manifest.ezra_version → "<EZRA_VERSION>") - may change with releases
    - Hash values (replaced with placeholders since they depend on timestamps)

    Preserves:
    - Structure (required keys, schema version)
    - Detection data
    - State structure
    - Hash structure (but not hash values)
    - File presence/absence

    Args:
        bundle_dir: Directory containing EPB bundle files.

    Returns:
        Normalized bundle structure as dict with file-based keys (e.g., "manifest.json").
    """
    # Read all files
    manifest_path = bundle_dir / "manifest.json"
    detections_path = bundle_dir / "detections.json"
    state_path = bundle_dir / "state.json"
    hashes_path = bundle_dir / "hashes.json"

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    detections = json.loads(detections_path.read_text(encoding="utf-8"))
    state = json.loads(state_path.read_text(encoding="utf-8"))
    hashes = json.loads(hashes_path.read_text(encoding="utf-8"))

    # Normalize manifest (replace non-deterministic fields with placeholders)
    normalized_manifest = {
        "epb_version": manifest["epb_version"],
        "ezra_version": "<EZRA_VERSION>",
        "input_metadata": manifest["input_metadata"],
        "plugin_versions": manifest["plugin_versions"],
        "platform": "<PLATFORM>",
        "python_version": "<PYTHON_VERSION>",
        "timestamp": "<TIMESTAMP>",
    }

    # Normalize state (replace timestamp with placeholder)
    normalized_state = {
        "version": state["version"],
        "timestamp": "<TIMESTAMP>",
    }

    # Normalize hashes (preserve structure, replace hash values with placeholders)
    # Hash values depend on timestamps, so we normalize them for contract comparison
    normalized_hashes = {
        "epb_version": hashes["epb_version"],
        "bundle_hash": hashes["bundle_hash"],  # Keep actual hash for structure validation
        "files": {
            filename: hashes["files"][filename]  # Keep actual hashes for structure validation
            for filename in sorted(hashes["files"].keys())
        },
    }

    result = {
        "manifest.json": normalized_manifest,
        "detections.json": detections,
        "state.json": normalized_state,
        "hashes.json": normalized_hashes,
    }

    # Include optional files if present
    delta_path = bundle_dir / "delta.json"
    if delta_path.exists():
        delta = json.loads(delta_path.read_text(encoding="utf-8"))
        # Normalize delta timestamp if present
        if "timestamp" in delta:
            delta_normalized = delta.copy()
            delta_normalized["timestamp"] = "<TIMESTAMP>"
            result["delta.json"] = delta_normalized
        else:
            result["delta.json"] = delta

    zones_path = bundle_dir / "zones.json"
    if zones_path.exists():
        zones = json.loads(zones_path.read_text(encoding="utf-8"))
        result["zones.json"] = zones

    return result


def test_epb_bundle_contract_structure(tmp_path: Path) -> None:
    """Test that EPB bundle structure matches contract (required files + keys)."""
    bundle = build_epb_bundle(
        detections=[{"text": "Hello", "confidence": 0.9, "bbox": [10.0, 20.0, 50.0, 40.0]}],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 200, "height": 100, "channels": 3},
        timestamp=FIXED_TIMESTAMP,
    )

    output_dir = tmp_path / "epb_contract"
    write_epb_bundle(bundle, output_dir)

    # Verify required files exist
    assert (output_dir / "manifest.json").exists()
    assert (output_dir / "detections.json").exists()
    assert (output_dir / "state.json").exists()
    assert (output_dir / "hashes.json").exists()

    # Verify manifest structure
    manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["epb_version"] == "1.0.0"
    assert "plugin_versions" in manifest
    assert "input_metadata" in manifest
    assert "timestamp" in manifest

    # Verify detections structure
    detections = json.loads((output_dir / "detections.json").read_text(encoding="utf-8"))
    assert "detections" in detections
    assert isinstance(detections["detections"], list)

    # Verify state structure
    state = json.loads((output_dir / "state.json").read_text(encoding="utf-8"))
    assert "version" in state
    assert "timestamp" in state

    # Verify hashes structure
    hashes = json.loads((output_dir / "hashes.json").read_text(encoding="utf-8"))
    assert hashes["epb_version"] == "1.0.0"
    assert "bundle_hash" in hashes
    assert "files" in hashes
    assert "manifest.json" in hashes["files"]
    assert "detections.json" in hashes["files"]
    assert "state.json" in hashes["files"]
    assert "hashes.json" in hashes["files"]


def test_epb_bundle_contract_snapshot(tmp_path: Path) -> None:
    """Test that EPB bundle normalized structure matches committed snapshot."""
    bundle = build_epb_bundle(
        detections=[{"text": "Hello", "confidence": 0.9, "bbox": [10.0, 20.0, 50.0, 40.0]}],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 200, "height": 100, "channels": 3},
        timestamp=FIXED_TIMESTAMP,
    )

    output_dir = tmp_path / "epb_snapshot"
    write_epb_bundle(bundle, output_dir)

    # Normalize bundle for snapshot comparison
    normalized = _normalize_epb_bundle_for_snapshot(output_dir)

    # Snapshot path
    snapshot_path = Path(__file__).parent / "snapshots" / "epb_bundle_contract_snapshot.json"

    if snapshot_path.exists():
        # Compare with committed snapshot
        snapshot_data = json.loads(snapshot_path.read_text(encoding="utf-8"))
        assert normalized == snapshot_data, "EPB bundle structure does not match snapshot"
    else:
        # First run: write snapshot
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        json_str = json.dumps(normalized, sort_keys=True, indent=2)
        snapshot_path.write_text(json_str + "\n", encoding="utf-8", newline="")
        # Re-read to verify
        snapshot_data = json.loads(snapshot_path.read_text(encoding="utf-8"))
        assert normalized == snapshot_data


def test_epb_bundle_deterministic_contract(tmp_path: Path) -> None:
    """Test that identical inputs produce identical EPB bundle outputs (determinism invariant)."""
    # Create identical bundles
    bundle1 = build_epb_bundle(
        detections=[{"text": "Hello", "confidence": 0.9, "bbox": [10.0, 20.0, 50.0, 40.0]}],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 200, "height": 100, "channels": 3},
        timestamp=FIXED_TIMESTAMP,
    )

    bundle2 = build_epb_bundle(
        detections=[{"text": "Hello", "confidence": 0.9, "bbox": [10.0, 20.0, 50.0, 40.0]}],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 200, "height": 100, "channels": 3},
        timestamp=FIXED_TIMESTAMP,
    )

    output_dir1 = tmp_path / "epb1"
    output_dir2 = tmp_path / "epb2"

    write_epb_bundle(bundle1, output_dir1)
    write_epb_bundle(bundle2, output_dir2)

    # Compare file contents (should be byte-identical)
    for filename in ["manifest.json", "detections.json", "state.json", "hashes.json"]:
        content1 = (output_dir1 / filename).read_text(encoding="utf-8")
        content2 = (output_dir2 / filename).read_text(encoding="utf-8")
        assert content1 == content2, f"{filename} differs between runs"

    # Compare hashes.json bundle_hash (should be identical)
    hashes1 = json.loads((output_dir1 / "hashes.json").read_text(encoding="utf-8"))
    hashes2 = json.loads((output_dir2 / "hashes.json").read_text(encoding="utf-8"))
    assert hashes1["bundle_hash"] == hashes2["bundle_hash"], "Bundle hash differs between runs"


def test_epb_bundle_schema_version_invariant(tmp_path: Path) -> None:
    """Test that EPB schema version (1.0.0) remains unchanged (artifact schema invariant)."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
        timestamp=FIXED_TIMESTAMP,
    )

    output_dir = tmp_path / "epb_schema"
    write_epb_bundle(bundle, output_dir)

    # Verify EPB version in all files
    manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["epb_version"] == "1.0.0"

    hashes = json.loads((output_dir / "hashes.json").read_text(encoding="utf-8"))
    assert hashes["epb_version"] == "1.0.0"

    state = json.loads((output_dir / "state.json").read_text(encoding="utf-8"))
    assert state["version"] == "1.0.0"
