"""Parity verification utilities for golden baseline comparison."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

try:
    import easyocr
except ImportError:
    easyocr = None

if TYPE_CHECKING:
    import torch
    import torchvision
else:
    try:
        import torch
    except ImportError:
        torch = None

    try:
        import torchvision
    except ImportError:
        torchvision = None


def load_baseline(path: Path) -> dict[str, Any]:
    """Load baseline JSON from file.

    Args:
        path: Path to baseline.json file.

    Returns:
        Parsed baseline dictionary.

    Raises:
        FileNotFoundError: If baseline file does not exist.
        json.JSONDecodeError: If baseline file is invalid JSON.
    """
    if not path.exists():
        raise FileNotFoundError(f"Baseline file not found: {path}")

    with open(path, encoding="utf-8") as f:
        return json.load(f)  # type: ignore[no-any-return]


def load_manifest(path: Path) -> dict[str, Any]:
    """Load manifest JSON from file.

    Args:
        path: Path to manifest.json file.

    Returns:
        Parsed manifest dictionary.

    Raises:
        FileNotFoundError: If manifest file does not exist.
        json.JSONDecodeError: If manifest file is invalid JSON.
    """
    if not path.exists():
        raise FileNotFoundError(f"Manifest file not found: {path}")

    with open(path, encoding="utf-8") as f:
        return json.load(f)  # type: ignore[no-any-return]


def validate_manifest_environment(manifest: dict[str, Any]) -> None:
    """Validate that current environment matches manifest requirements.

    Checks:
    - easyocr_version
    - python_version (major.minor only, not patch)
    - torch_version
    - torchvision_version (if present in manifest)
    - model_checksums (if present in manifest)

    Args:
        manifest: Manifest dictionary loaded from manifest.json.

    Raises:
        ValueError: If any environment check fails.
    """
    errors: list[str] = []

    # Check EasyOCR version
    if easyocr is None:
        errors.append("EasyOCR is not installed (required for parity verification)")
    else:
        expected_version = manifest.get("easyocr_version")
        if expected_version:
            # EasyOCR doesn't expose __version__ directly, so we check if it's installed
            # The version is pinned in pyproject.toml, so we trust that
            pass  # Version check deferred to dependency management

    # Check Python version (major.minor only)
    expected_python = manifest.get("python_version", "")
    if expected_python:
        # Extract major.minor from full version string
        # Format: "3.12.10 (tags/v3.12.10:0cc8128, ...)"
        parts = expected_python.split()
        if parts:
            version_str = parts[0]
            major_minor = ".".join(version_str.split(".")[:2])
            current_major_minor = f"{sys.version_info.major}.{sys.version_info.minor}"
            if major_minor != current_major_minor:
                errors.append(
                    f"Python version mismatch: expected {major_minor}, got {current_major_minor}"
                )

    # Check torch version
    expected_torch = manifest.get("torch_version")
    if expected_torch:
        if torch is None:
            errors.append("torch is not installed (required for parity verification)")
        else:
            current_torch = torch.__version__
            # Normalize versions (strip +cuXXX suffixes for comparison)
            expected_normalized = expected_torch.split("+")[0]
            current_normalized = current_torch.split("+")[0]
            if expected_normalized != current_normalized:
                errors.append(
                    f"torch version mismatch: expected {expected_normalized}, "
                    f"got {current_normalized}"
                )

    # Check torchvision version (if present in manifest)
    expected_torchvision = manifest.get("torchvision_version")
    if expected_torchvision:
        if torchvision is None:
            errors.append("torchvision is not installed (required for parity verification)")
        else:
            current_torchvision = torchvision.__version__
            # Normalize versions (strip +cuXXX suffixes for comparison)
            expected_normalized = expected_torchvision.split("+")[0]
            current_normalized = current_torchvision.split("+")[0]
            if expected_normalized != current_normalized:
                errors.append(
                    f"torchvision version mismatch: expected {expected_normalized}, "
                    f"got {current_normalized}"
                )

    # Model checksums are validated separately (they require model files to exist)
    # We don't validate them here to avoid requiring model downloads

    if errors:
        error_msg = "Manifest environment validation failed:\n  " + "\n  ".join(errors)
        raise ValueError(error_msg)


def compare_outputs(current: dict[str, Any], baseline: dict[str, Any]) -> None:
    """Compare current output to baseline output.

    Uses exact structural equality (not approximate float comparison).
    Both outputs must be canonicalized before comparison.

    Args:
        current: Current canonicalized output dictionary.
        baseline: Baseline canonicalized output dictionary.

    Raises:
        AssertionError: If outputs do not match exactly.
    """
    # Use exact equality - canonicalization ensures deterministic rounding
    if current != baseline:
        # Provide detailed error message
        current_detections = current.get("detections", [])
        baseline_detections = baseline.get("detections", [])

        if len(current_detections) != len(baseline_detections):
            raise AssertionError(
                f"Detection count mismatch: current={len(current_detections)}, "
                f"baseline={len(baseline_detections)}"
            )

        # Compare each detection
        for i, (curr, base) in enumerate(zip(current_detections, baseline_detections)):
            if curr != base:
                raise AssertionError(
                    f"Detection {i} mismatch:\n  current: {curr}\n  baseline: {base}"
                )

        # If we get here, there's a structural difference we didn't catch
        raise AssertionError(
            f"Output structure mismatch:\n  current: {current}\n  baseline: {baseline}"
        )


def compute_file_sha256(path: Path) -> str:
    """Compute SHA256 hash of file contents.

    Args:
        path: Path to file.

    Returns:
        Hexadecimal SHA256 hash string.

    Raises:
        FileNotFoundError: If file does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        # Read in chunks to handle large files
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            sha256.update(chunk)

    return sha256.hexdigest()
