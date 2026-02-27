"""Tests for EPB bundle hash verification."""

import json
from pathlib import Path

import pytest

from ezra.epb import build_epb_bundle, verify_epb_bundle, write_epb_bundle


def test_verify_valid_bundle_passes(tmp_path: Path) -> None:
    """Test that a valid EPB bundle passes verification."""
    bundle = build_epb_bundle(
        detections=[{"text": "Hello", "confidence": 0.9, "bbox": [10.0, 20.0, 50.0, 40.0]}],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    output_dir = tmp_path / "epb"
    write_epb_bundle(bundle, output_dir)

    # Verification should pass (called automatically by write_epb_bundle)
    # But we can also call it explicitly to test the function
    verify_epb_bundle(output_dir)


def test_verify_valid_bundle_with_delta_passes(tmp_path: Path) -> None:
    """Test that a valid EPB bundle with delta passes verification."""
    delta = {
        "version": "1.0.0",
        "previous_bundle_hash": "0" * 64,
        "timestamp": "2024-01-01T00:00:00Z",
    }
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
        delta=delta,
    )

    output_dir = tmp_path / "epb"
    write_epb_bundle(bundle, output_dir)

    # Verification should pass
    verify_epb_bundle(output_dir)


def test_verify_detects_tampered_manifest(tmp_path: Path) -> None:
    """Test that verification detects tampered manifest.json."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    output_dir = tmp_path / "epb"
    write_epb_bundle(bundle, output_dir)

    # Tamper manifest.json
    manifest_path = output_dir / "manifest.json"
    manifest_content = manifest_path.read_text(encoding="utf-8")
    manifest = json.loads(manifest_content)
    manifest["epb_version"] = "2.0.0"  # Tamper
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    # Verification should fail
    with pytest.raises(ValueError, match="manifest.json hash mismatch"):
        verify_epb_bundle(output_dir)


def test_verify_detects_tampered_detections(tmp_path: Path) -> None:
    """Test that verification detects tampered detections.json."""
    bundle = build_epb_bundle(
        detections=[{"text": "Hello", "confidence": 0.9, "bbox": [10.0, 20.0, 50.0, 40.0]}],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    output_dir = tmp_path / "epb"
    write_epb_bundle(bundle, output_dir)

    # Tamper detections.json
    detections_path = output_dir / "detections.json"
    detections_content = detections_path.read_text(encoding="utf-8")
    detections = json.loads(detections_content)
    detections["detections"][0]["text"] = "Tampered"  # Tamper
    detections_path.write_text(json.dumps(detections, indent=2) + "\n", encoding="utf-8")

    # Verification should fail
    with pytest.raises(ValueError, match="detections.json hash mismatch"):
        verify_epb_bundle(output_dir)


def test_verify_detects_tampered_state(tmp_path: Path) -> None:
    """Test that verification detects tampered state.json."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    output_dir = tmp_path / "epb"
    write_epb_bundle(bundle, output_dir)

    # Tamper state.json
    state_path = output_dir / "state.json"
    state_content = state_path.read_text(encoding="utf-8")
    state = json.loads(state_content)
    state["tampered"] = True  # Tamper
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    # Verification should fail
    with pytest.raises(ValueError, match="state.json hash mismatch"):
        verify_epb_bundle(output_dir)


def test_verify_detects_tampered_delta(tmp_path: Path) -> None:
    """Test that verification detects tampered delta.json."""
    delta = {
        "version": "1.0.0",
        "previous_bundle_hash": "0" * 64,
        "timestamp": "2024-01-01T00:00:00Z",
    }
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
        delta=delta,
    )

    output_dir = tmp_path / "epb"
    write_epb_bundle(bundle, output_dir)

    # Tamper delta.json
    delta_path = output_dir / "delta.json"
    delta_content = delta_path.read_text(encoding="utf-8")
    delta_dict = json.loads(delta_content)
    delta_dict["previous_bundle_hash"] = "1" * 64  # Tamper
    delta_path.write_text(json.dumps(delta_dict, indent=2) + "\n", encoding="utf-8")

    # Verification should fail
    with pytest.raises(ValueError, match="delta.json hash mismatch"):
        verify_epb_bundle(output_dir)


def test_verify_detects_missing_file(tmp_path: Path) -> None:
    """Test that verification detects missing file declared in hashes.json."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    output_dir = tmp_path / "epb"
    write_epb_bundle(bundle, output_dir)

    # Delete a required file
    (output_dir / "manifest.json").unlink()

    # Verification should fail
    with pytest.raises(ValueError, match="missing on disk"):
        verify_epb_bundle(output_dir)


def test_verify_detects_bundle_hash_mismatch(tmp_path: Path) -> None:
    """Test that verification detects bundle_hash mismatch."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    output_dir = tmp_path / "epb"
    write_epb_bundle(bundle, output_dir)

    # Tamper hashes.json bundle_hash
    hashes_path = output_dir / "hashes.json"
    hashes_content = hashes_path.read_text(encoding="utf-8")
    hashes = json.loads(hashes_content)
    hashes["bundle_hash"] = "0" * 64  # Tamper bundle_hash
    hashes_path.write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")

    # Verification should fail
    with pytest.raises(ValueError, match="bundle_hash mismatch"):
        verify_epb_bundle(output_dir)


def test_verify_detects_hashes_json_self_hash_mismatch(tmp_path: Path) -> None:
    """Test that verification detects hashes.json self-hash mismatch."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    output_dir = tmp_path / "epb"
    write_epb_bundle(bundle, output_dir)

    # Tamper hashes.json self-hash entry
    hashes_path = output_dir / "hashes.json"
    hashes_content = hashes_path.read_text(encoding="utf-8")
    hashes = json.loads(hashes_content)
    hashes["files"]["hashes.json"] = "0" * 64  # Tamper self-hash
    hashes_path.write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")

    # Verification should fail
    with pytest.raises(ValueError, match="hashes.json self-hash mismatch"):
        verify_epb_bundle(output_dir)


def test_verify_ignores_extra_files(tmp_path: Path) -> None:
    """Test that verification ignores extra files not in hashes.json."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    output_dir = tmp_path / "epb"
    write_epb_bundle(bundle, output_dir)

    # Add extra file not in hashes.json
    extra_file = output_dir / "extra.json"
    extra_file.write_text('{"extra": true}\n', encoding="utf-8")

    # Verification should pass (extra files are ignored)
    verify_epb_bundle(output_dir)


def test_verify_missing_hashes_json_fails(tmp_path: Path) -> None:
    """Test that verification fails if hashes.json is missing."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    output_dir = tmp_path / "epb"
    write_epb_bundle(bundle, output_dir)

    # Delete hashes.json
    (output_dir / "hashes.json").unlink()

    # Verification should fail
    with pytest.raises(ValueError, match="missing hashes.json"):
        verify_epb_bundle(output_dir)


def test_verify_invalid_hashes_json_fails(tmp_path: Path) -> None:
    """Test that verification fails if hashes.json is invalid JSON."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    output_dir = tmp_path / "epb"
    write_epb_bundle(bundle, output_dir)

    # Corrupt hashes.json
    hashes_path = output_dir / "hashes.json"
    hashes_path.write_text("invalid json content\n", encoding="utf-8")

    # Verification should fail
    with pytest.raises(ValueError, match="invalid JSON"):
        verify_epb_bundle(output_dir)


def test_verify_missing_files_field_fails(tmp_path: Path) -> None:
    """Test that verification fails if hashes.json missing 'files' field."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    output_dir = tmp_path / "epb"
    write_epb_bundle(bundle, output_dir)

    # Remove 'files' field from hashes.json
    hashes_path = output_dir / "hashes.json"
    hashes_content = hashes_path.read_text(encoding="utf-8")
    hashes = json.loads(hashes_content)
    del hashes["files"]
    hashes_path.write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")

    # Verification should fail
    with pytest.raises(ValueError, match="missing 'files' field"):
        verify_epb_bundle(output_dir)
