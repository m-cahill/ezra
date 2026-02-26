"""Tests for baseline artifact schema validation."""

import json
from pathlib import Path

import pytest

from ezra.baseline.canonicalize import to_canonical_json


def test_baseline_files_exist() -> None:
    """Test that baseline files exist in expected location."""
    baseline_dir = Path("docs/baselines/easyocr/1.7.2/synthetic_basic")
    baseline_file = baseline_dir / "baseline.json"
    manifest_file = baseline_dir / "manifest.json"

    # These files may not exist until baseline is captured
    # This test documents the expected location
    if not baseline_file.exists():
        pytest.skip("Baseline not yet captured. Run: python -m ezra.tools.capture_easyocr_baseline")

    assert baseline_file.exists(), f"Baseline file not found: {baseline_file}"
    assert manifest_file.exists(), f"Manifest file not found: {manifest_file}"


def test_baseline_json_schema() -> None:
    """Test that baseline.json matches expected schema."""
    baseline_file = Path("docs/baselines/easyocr/1.7.2/synthetic_basic/baseline.json")

    if not baseline_file.exists():
        pytest.skip("Baseline not yet captured. Run: python -m ezra.tools.capture_easyocr_baseline")

    with open(baseline_file, encoding="utf-8") as f:
        baseline = json.load(f)

    # Schema: {"detections": [...]}
    assert "detections" in baseline
    assert isinstance(baseline["detections"], list)

    # Each detection should have: text, confidence, bbox
    for det in baseline["detections"]:
        assert "text" in det
        assert "confidence" in det
        assert "bbox" in det

        assert isinstance(det["text"], str)
        assert isinstance(det["confidence"], (int, float))
        assert isinstance(det["bbox"], list)
        assert len(det["bbox"]) == 4
        assert all(isinstance(coord, (int, float)) for coord in det["bbox"])


def test_manifest_json_schema() -> None:
    """Test that manifest.json matches expected schema."""
    manifest_file = Path("docs/baselines/easyocr/1.7.2/synthetic_basic/manifest.json")

    if not manifest_file.exists():
        pytest.skip("Baseline not yet captured. Run: python -m ezra.tools.capture_easyocr_baseline")

    with open(manifest_file, encoding="utf-8") as f:
        manifest = json.load(f)

    # Required fields
    assert "python_version" in manifest
    assert "platform" in manifest
    assert "easyocr_version" in manifest
    assert "torch_version" in manifest
    assert "torchvision_version" in manifest
    assert "model_checksums" in manifest
    assert "fixture_set" in manifest
    assert "device" in manifest

    # Types
    assert isinstance(manifest["python_version"], str)
    assert isinstance(manifest["platform"], str)
    assert manifest["easyocr_version"] == "1.7.2"
    assert isinstance(manifest["model_checksums"], dict)
    assert manifest["fixture_set"] == "synthetic_basic"
    assert manifest["device"] == "cpu"


def test_baseline_deterministic_format() -> None:
    """Test that baseline.json is in canonical format (sorted, rounded)."""
    baseline_file = Path("docs/baselines/easyocr/1.7.2/synthetic_basic/baseline.json")

    if not baseline_file.exists():
        pytest.skip("Baseline not yet captured. Run: python -m ezra.tools.capture_easyocr_baseline")

    with open(baseline_file, encoding="utf-8") as f:
        content = f.read()

    # Parse and re-serialize to check canonical format
    baseline = json.loads(content)
    canonical_content = to_canonical_json(baseline)

    # Should match (allowing for minor whitespace differences)
    baseline_parsed = json.loads(content)
    canonical_parsed = json.loads(canonical_content)

    assert baseline_parsed == canonical_parsed
