"""Tests for EPB JSON Schema validation."""

from pathlib import Path

import pytest

from ezra.epb import build_epb_bundle, validate_bundle, write_epb_bundle


def test_valid_bundle_passes_schema_validation() -> None:
    """Test that a valid EPB bundle passes schema validation."""
    bundle = build_epb_bundle(
        detections=[{"text": "Hello", "confidence": 0.9, "bbox": [10.0, 20.0, 50.0, 40.0]}],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    # Should not raise
    validate_bundle(bundle)


def test_valid_bundle_with_state_passes_validation() -> None:
    """Test that a valid bundle with structured state passes validation."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
        state={
            "zones": [
                {
                    "id": "zone1",
                    "bbox": [0.0, 0.0, 100.0, 100.0],
                    "type": "text",
                    "content": "Test zone",
                }
            ]
        },
    )

    # Should not raise
    validate_bundle(bundle)


def test_valid_bundle_with_delta_passes_validation() -> None:
    """Test that a valid bundle with delta passes validation."""
    delta = {
        "version": "1.0.0",
        "previous_bundle_hash": "a" * 64,  # 64-char hex string
        "timestamp": "2024-01-01T00:00:00Z",
    }
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
        delta=delta,
    )

    # Should not raise
    validate_bundle(bundle)


def test_invalid_manifest_fails_validation() -> None:
    """Test that invalid manifest structure fails validation."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    # Remove required field
    del bundle["manifest"]["epb_version"]

    with pytest.raises(ValueError, match="EPB manifest validation failed"):
        validate_bundle(bundle)


def test_invalid_detections_fails_validation() -> None:
    """Test that invalid detections structure fails validation."""
    bundle = build_epb_bundle(
        detections=[{"text": "Hello", "confidence": 0.9, "bbox": [10.0, 20.0, 50.0, 40.0]}],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    # Add invalid detection (missing required field)
    bundle["detections"]["detections"].append({"text": "Invalid"})  # Missing bbox

    with pytest.raises(ValueError, match="EPB detections validation failed"):
        validate_bundle(bundle)


def test_invalid_state_fails_validation() -> None:
    """Test that invalid state structure fails validation."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
        state={"zones": [{"id": "zone1"}]},  # Missing required bbox
    )

    with pytest.raises(ValueError, match="EPB state validation failed"):
        validate_bundle(bundle)


def test_invalid_delta_fails_validation() -> None:
    """Test that invalid delta structure fails validation."""
    # Invalid delta (missing required fields)
    delta = {"version": "1.0.0"}  # Missing previous_bundle_hash and timestamp
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
        delta=delta,
    )

    with pytest.raises(ValueError, match="EPB delta validation failed"):
        validate_bundle(bundle)


def test_schema_validator_raises_on_missing_required_field() -> None:
    """Test that missing required fields raise ValueError."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    # Remove required field from manifest
    del bundle["manifest"]["timestamp"]

    with pytest.raises(ValueError, match="EPB manifest validation failed"):
        validate_bundle(bundle)


def test_write_epb_bundle_validates_before_writing(tmp_path: Path) -> None:
    """Test that write_epb_bundle validates before writing files."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    # Corrupt bundle
    bundle["manifest"]["epb_version"] = "invalid-version"

    output_dir = tmp_path / "epb"

    # Should fail before writing any files
    with pytest.raises(ValueError, match="EPB manifest validation failed"):
        write_epb_bundle(bundle, output_dir)

    # No files should be written
    assert not (output_dir / "manifest.json").exists()
    assert not (output_dir / "hashes.json").exists()


def test_invalid_detection_bbox_fails_validation() -> None:
    """Test that invalid bbox structure fails validation."""
    bundle = build_epb_bundle(
        detections=[
            {"text": "Hello", "confidence": 0.9, "bbox": [10.0, 20.0]}  # Wrong length
        ],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    with pytest.raises(ValueError, match="EPB detections validation failed"):
        validate_bundle(bundle)


def test_invalid_confidence_range_fails_validation() -> None:
    """Test that confidence outside [0.0, 1.0] fails validation."""
    bundle = build_epb_bundle(
        detections=[
            {"text": "Hello", "confidence": 1.5, "bbox": [10.0, 20.0, 50.0, 40.0]}  # > 1.0
        ],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    with pytest.raises(ValueError, match="EPB detections validation failed"):
        validate_bundle(bundle)
