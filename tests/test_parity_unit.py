"""Unit tests for parity verification utilities (no EasyOCR required)."""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from ezra.baseline.parity import (
    compare_outputs,
    compute_file_sha256,
    load_baseline,
    load_manifest,
    validate_manifest_environment,
)


def test_load_baseline() -> None:
    """Test loading baseline JSON from file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        baseline_data = {
            "detections": [{"text": "test", "confidence": 0.9, "bbox": [0, 0, 10, 10]}]
        }
        json.dump(baseline_data, f)
        temp_path = Path(f.name)

    try:
        loaded = load_baseline(temp_path)
        assert loaded == baseline_data
    finally:
        temp_path.unlink()


def test_load_baseline_not_found() -> None:
    """Test that load_baseline raises FileNotFoundError for missing file."""
    with pytest.raises(FileNotFoundError):
        load_baseline(Path("nonexistent.json"))


def test_load_manifest() -> None:
    """Test loading manifest JSON from file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        manifest_data = {
            "python_version": "3.12.0",
            "platform": "test",
            "easyocr_version": "1.7.2",
        }
        json.dump(manifest_data, f)
        temp_path = Path(f.name)

    try:
        loaded = load_manifest(temp_path)
        assert loaded == manifest_data
    finally:
        temp_path.unlink()


def test_load_manifest_not_found() -> None:
    """Test that load_manifest raises FileNotFoundError for missing file."""
    with pytest.raises(FileNotFoundError):
        load_manifest(Path("nonexistent.json"))


def test_compare_outputs_match() -> None:
    """Test that compare_outputs passes for identical outputs."""
    output = {"detections": [{"text": "test", "confidence": 0.9, "bbox": [0, 0, 10, 10]}]}
    compare_outputs(output, output)  # Should not raise


def test_compare_outputs_different_count() -> None:
    """Test that compare_outputs fails for different detection counts."""
    current = {"detections": [{"text": "test", "confidence": 0.9, "bbox": [0, 0, 10, 10]}]}
    baseline = {"detections": []}

    with pytest.raises(AssertionError, match="Detection count mismatch"):
        compare_outputs(current, baseline)


def test_compare_outputs_different_detection() -> None:
    """Test that compare_outputs fails for different detections."""
    current = {"detections": [{"text": "test1", "confidence": 0.9, "bbox": [0, 0, 10, 10]}]}
    baseline = {"detections": [{"text": "test2", "confidence": 0.9, "bbox": [0, 0, 10, 10]}]}

    with pytest.raises(AssertionError, match="Detection 0 mismatch"):
        compare_outputs(current, baseline)


def test_compute_file_sha256() -> None:
    """Test SHA256 hash computation."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("test content")
        temp_path = Path(f.name)

    try:
        hash_value = compute_file_sha256(temp_path)
        assert len(hash_value) == 64  # SHA256 hex digest is 64 chars
        assert isinstance(hash_value, str)
    finally:
        temp_path.unlink()


def test_compute_file_sha256_not_found() -> None:
    """Test that compute_file_sha256 raises FileNotFoundError for missing file."""
    with pytest.raises(FileNotFoundError):
        compute_file_sha256(Path("nonexistent.txt"))


def test_compute_file_sha256_deterministic() -> None:
    """Test that SHA256 hash is deterministic."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("test content")
        temp_path = Path(f.name)

    try:
        hash1 = compute_file_sha256(temp_path)
        hash2 = compute_file_sha256(temp_path)
        assert hash1 == hash2
    finally:
        temp_path.unlink()


def test_validate_manifest_environment_success() -> None:
    """Test that validate_manifest_environment passes for matching environment."""
    manifest = {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.0",
    }

    # Mock easyocr as available (installed)
    with patch("ezra.baseline.parity.easyocr", object()):
        # Should not raise if environment matches
        validate_manifest_environment(manifest)


def test_validate_manifest_environment_python_mismatch() -> None:
    """Test that validate_manifest_environment fails for Python version mismatch."""
    manifest = {
        "python_version": "99.99.0 (fake version)",
        "easyocr_version": "1.7.2",
    }

    with pytest.raises(ValueError, match="Python version mismatch"):
        validate_manifest_environment(manifest)


def test_validate_manifest_environment_torch_mismatch() -> None:
    """Test that validate_manifest_environment fails for torch version mismatch."""
    manifest = {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.0",
        "torch_version": "99.99.99",
    }

    # Mock torch to return different version
    with patch("ezra.baseline.parity.torch") as mock_torch:
        mock_torch.__version__ = "1.0.0"
        with pytest.raises(ValueError, match="torch version mismatch"):
            validate_manifest_environment(manifest)


def test_validate_manifest_environment_torchvision_mismatch() -> None:
    """Test that validate_manifest_environment fails for torchvision version mismatch."""
    manifest = {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.0",
        "torchvision_version": "99.99.99",
    }

    # Mock torchvision to return different version
    with patch("ezra.baseline.parity.torchvision") as mock_torchvision:
        mock_torchvision.__version__ = "1.0.0"
        with pytest.raises(ValueError, match="torchvision version mismatch"):
            validate_manifest_environment(manifest)


def test_validate_manifest_environment_torch_not_installed() -> None:
    """Test that validate_manifest_environment fails when torch not installed but required."""
    manifest = {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.0",
        "torch_version": "2.0.0",
    }

    # Mock torch as None (not installed)
    with patch("ezra.baseline.parity.torch", None):
        with pytest.raises(ValueError, match="torch is not installed"):
            validate_manifest_environment(manifest)
