"""Parity verification tests for golden baseline comparison.

These tests verify that EasyOCRPlugin output matches the committed golden baseline.
All tests are marked as integration and parity tests, and require EZRA_RUN_PARITY=1 to run.
"""

import os
from pathlib import Path

import numpy as np
import pytest

from ezra.baseline.canonicalize import canonicalize_output
from ezra.baseline.parity import (
    compare_outputs,
    compute_file_sha256,
    load_baseline,
    load_manifest,
    validate_manifest_environment,
)

# Expected SHA256 hash of baseline.json (computed from committed file)
# This hash locks the baseline file - any modification will fail the test
EXPECTED_BASELINE_SHA256 = "3157ebb21c5382221a22acaed154611172122ef6aab188b0bf15e02a5a018e60"

# Baseline directory path
BASELINE_DIR = Path("docs/baselines/easyocr/1.7.2/synthetic_basic")
BASELINE_FILE = BASELINE_DIR / "baseline.json"
MANIFEST_FILE = BASELINE_DIR / "manifest.json"


def _should_run_parity() -> bool:
    """Check if parity tests should run."""
    return os.getenv("EZRA_RUN_PARITY") == "1"


def _generate_synthetic_fixture(text: str, width: int = 200, height: int = 50) -> np.ndarray:
    """Generate synthetic text image (same logic as capture tool).

    Args:
        text: Text to render.
        width: Image width in pixels.
        height: Image height in pixels.

    Returns:
        numpy array representation of image.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        pytest.skip("PIL (Pillow) is required for parity tests")

    # Create white background
    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)

    # Try to use default font, fallback to basic if not available
    font = None
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except OSError:
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None

    # Calculate text position (centered)
    if font:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    else:
        text_width = len(text) * 24 // 2
        text_height = 24

    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # Draw black text
    draw.text((x, y), text, fill="black", font=font)

    # Convert to numpy array
    return np.array(img)


@pytest.mark.integration
@pytest.mark.parity
def test_parity_matches_baseline() -> None:
    """Test that current EasyOCRPlugin output matches committed baseline.

    This test:
    1. Loads the committed baseline.json
    2. Re-runs EasyOCRPlugin on the same synthetic fixtures
    3. Canonicalizes the current output
    4. Compares to baseline using exact equality

    Requires EZRA_RUN_PARITY=1 to run.
    """
    if not _should_run_parity():
        pytest.skip("Parity tests require EZRA_RUN_PARITY=1")

    if not BASELINE_FILE.exists():
        pytest.skip("Baseline not captured. Run: python -m ezra.tools.capture_easyocr_baseline")

    try:
        from ezra.plugins.easyocr_plugin import EasyOCRPlugin
    except ImportError:
        pytest.skip("EasyOCR is not installed (required for parity tests)")

    # Load baseline
    baseline = load_baseline(BASELINE_FILE)

    # Generate same fixtures as capture tool
    fixtures = [
        ("Hello", 200, 50),
        ("World", 200, 50),
        ("EZRA", 200, 50),
        ("123", 150, 50),
    ]

    # Initialize plugin (same config as baseline capture)
    plugin = EasyOCRPlugin(device="cpu", languages=["en"])
    plugin.load("")

    # Run inference on all fixtures
    all_detections = []
    for text, width, height in fixtures:
        img_array = _generate_synthetic_fixture(text, width, height)
        result = plugin.infer(img_array)
        all_detections.extend(result["detections"])

    # Canonicalize output
    current_output = canonicalize_output({"detections": all_detections})

    # Compare to baseline (exact equality)
    compare_outputs(current_output, baseline)


@pytest.mark.integration
@pytest.mark.parity
def test_manifest_matches_environment() -> None:
    """Test that current environment matches manifest requirements.

    Validates:
    - easyocr_version (presence check)
    - python_version (major.minor)
    - torch_version
    - torchvision_version (if present)

    Requires EZRA_RUN_PARITY=1 to run.
    """
    if not _should_run_parity():
        pytest.skip("Parity tests require EZRA_RUN_PARITY=1")

    if not MANIFEST_FILE.exists():
        pytest.skip("Manifest not found. Run: python -m ezra.tools.capture_easyocr_baseline")

    # Load manifest
    manifest = load_manifest(MANIFEST_FILE)

    # Validate environment matches manifest
    validate_manifest_environment(manifest)


@pytest.mark.integration
@pytest.mark.parity
def test_canonicalization_stable_multiple_runs() -> None:
    """Test that canonicalization produces identical output across multiple runs.

    Runs canonicalization 5 times on the same input and asserts bitwise equality.
    This ensures canonicalization is deterministic and stable.

    Requires EZRA_RUN_PARITY=1 to run.
    """
    if not _should_run_parity():
        pytest.skip("Parity tests require EZRA_RUN_PARITY=1")

    if not BASELINE_FILE.exists():
        pytest.skip("Baseline not captured. Run: python -m ezra.tools.capture_easyocr_baseline")

    # Load baseline to get a real detection structure
    baseline = load_baseline(BASELINE_FILE)
    detections = baseline.get("detections", [])

    if not detections:
        pytest.skip("Baseline has no detections to test")

    # Run canonicalization 5 times
    results = []
    for _ in range(5):
        canonicalized = canonicalize_output({"detections": detections})
        results.append(canonicalized)

    # Assert all results are identical (bitwise equality)
    first_result = results[0]
    for i, result in enumerate(results[1:], start=1):
        assert result == first_result, f"Canonicalization run {i + 1} differs from run 1"


@pytest.mark.integration
@pytest.mark.parity
def test_baseline_file_hash_stable() -> None:
    """Test that baseline.json file hash matches expected value.

    This test locks the baseline file - any modification (even whitespace) will fail.
    If baseline intentionally changes, this hash must be updated in a new milestone.

    Requires EZRA_RUN_PARITY=1 to run.
    """
    if not _should_run_parity():
        pytest.skip("Parity tests require EZRA_RUN_PARITY=1")

    if not BASELINE_FILE.exists():
        pytest.skip("Baseline not captured. Run: python -m ezra.tools.capture_easyocr_baseline")

    # Compute current hash
    current_hash = compute_file_sha256(BASELINE_FILE)

    # Compare to expected hash
    assert current_hash == EXPECTED_BASELINE_SHA256, (
        f"Baseline file hash mismatch. Expected: {EXPECTED_BASELINE_SHA256}, Got: {current_hash}"
    )
