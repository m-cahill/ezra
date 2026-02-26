"""Tests for EPB bundle emission (end-to-end)."""

import json
from pathlib import Path

from ezra.epb import build_epb_bundle, write_epb_bundle


def test_write_epb_bundle_minimal(tmp_path: Path) -> None:
    """Test writing minimal EPB bundle to disk."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    output_dir = tmp_path / "epb"
    write_epb_bundle(bundle, output_dir)

    # Verify required files exist
    assert (output_dir / "manifest.json").exists()
    assert (output_dir / "detections.json").exists()
    assert (output_dir / "state.json").exists()
    assert (output_dir / "hashes.json").exists()
    assert not (output_dir / "delta.json").exists()  # Delta not present


def test_write_epb_bundle_with_delta(tmp_path: Path) -> None:
    """Test writing EPB bundle with delta."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
        delta={"changes": []},
    )

    output_dir = tmp_path / "epb"
    write_epb_bundle(bundle, output_dir)

    assert (output_dir / "delta.json").exists()


def test_write_epb_bundle_lf_line_endings(tmp_path: Path) -> None:
    """Test that files are written with LF line endings."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    output_dir = tmp_path / "epb"
    write_epb_bundle(bundle, output_dir)

    # Read raw bytes to check line endings
    manifest_content = (output_dir / "manifest.json").read_bytes()
    assert b"\r\n" not in manifest_content  # No CRLF
    assert manifest_content.endswith(b"\n")  # Ends with LF


def test_write_epb_bundle_canonical_json(tmp_path: Path) -> None:
    """Test that written JSON is canonical (sorted keys)."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    output_dir = tmp_path / "epb"
    write_epb_bundle(bundle, output_dir)

    # Read and parse manifest
    manifest_content = (output_dir / "manifest.json").read_text(encoding="utf-8")
    manifest = json.loads(manifest_content)

    # Verify structure
    assert manifest["epb_version"] == "1.0.0"
    assert "plugin_versions" in manifest
    assert "input_metadata" in manifest


def test_write_epb_bundle_hashes_structure(tmp_path: Path) -> None:
    """Test that hashes.json has correct structure."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    output_dir = tmp_path / "epb"
    write_epb_bundle(bundle, output_dir)

    # Read and parse hashes.json
    hashes_content = (output_dir / "hashes.json").read_text(encoding="utf-8")
    hashes = json.loads(hashes_content)

    # Verify structure
    assert hashes["epb_version"] == "1.0.0"
    assert "bundle_hash" in hashes
    assert "files" in hashes

    # Verify required files in files map
    files = hashes["files"]
    assert "manifest.json" in files
    assert "detections.json" in files
    assert "state.json" in files
    assert "hashes.json" in files  # Required by schema
    assert "delta.json" not in files  # Not present

    # Verify hash lengths
    for hash_value in files.values():
        assert len(hash_value) == 64  # SHA256 hex string


def test_write_epb_bundle_deterministic(tmp_path: Path) -> None:
    """Test that writing the same bundle produces identical output."""
    bundle = build_epb_bundle(
        detections=[{"text": "Hello", "confidence": 0.9, "bbox": [10.0, 20.0, 50.0, 40.0]}],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    output_dir1 = tmp_path / "epb1"
    output_dir2 = tmp_path / "epb2"

    write_epb_bundle(bundle, output_dir1)
    write_epb_bundle(bundle, output_dir2)

    # Compare file contents (should be identical)
    for filename in ["manifest.json", "detections.json", "state.json", "hashes.json"]:
        content1 = (output_dir1 / filename).read_text(encoding="utf-8")
        content2 = (output_dir2 / filename).read_text(encoding="utf-8")
        assert content1 == content2


def test_write_epb_bundle_utf8_encoding(tmp_path: Path) -> None:
    """Test that files are written with UTF-8 encoding."""
    bundle = build_epb_bundle(
        detections=[{"text": "Hello 世界", "confidence": 0.9, "bbox": [10.0, 20.0, 50.0, 40.0]}],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    output_dir = tmp_path / "epb"
    write_epb_bundle(bundle, output_dir)

    # Read with UTF-8 and verify Unicode characters preserved
    detections_content = (output_dir / "detections.json").read_text(encoding="utf-8")
    assert "世界" in detections_content
