"""Baseline capture tool for EasyOCR golden outputs.

This tool runs EasyOCR on synthetic fixtures and captures canonical outputs
for regression testing. Run locally (not in CI) to generate baseline artifacts.
"""

from __future__ import annotations

import hashlib
import platform
import sys
from pathlib import Path
from typing import Any

try:
    import easyocr
except ImportError:
    easyocr = None  # type: ignore[assignment, misc]

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = None  # type: ignore[assignment, misc]
    ImageDraw = None  # type: ignore[assignment, misc]
    ImageFont = None  # type: ignore[assignment, misc]

from ezra.baseline.canonicalize import canonicalize_output, to_canonical_json
from ezra.plugins.easyocr_plugin import EasyOCRPlugin


def generate_synthetic_fixture(
    text: str, width: int = 200, height: int = 50, font_size: int = 24
) -> Any:
    """Generate a synthetic text image using PIL.

    Args:
        text: Text to render.
        width: Image width in pixels.
        height: Image height in pixels.
        font_size: Font size in points.

    Returns:
        PIL Image object.

    Raises:
        ImportError: If PIL is not available.
    """
    if Image is None or ImageDraw is None or ImageFont is None:
        msg = (
            "PIL (Pillow) is required for fixture generation. "
            "Install with: pip install -e '.[dev]'"
        )
        raise ImportError(msg)

    # Create white background
    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)

    # Try to use default font, fallback to basic if not available
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
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
        # Rough estimate if font unavailable
        text_width = len(text) * font_size // 2
        text_height = font_size

    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # Draw black text
    draw.text((x, y), text, fill="black", font=font)

    return img


def get_model_checksums() -> dict[str, str]:
    """Attempt to discover and hash EasyOCR model files.

    Returns:
        Dictionary mapping model file names to SHA256 checksums.
        Empty dict if models cannot be found.
    """
    checksums: dict[str, str] = {}

    if easyocr is None:
        return checksums

    # EasyOCR stores models in user directory
    # Try to find the model directory
    try:
        user_home = Path.home()
        # Common EasyOCR model locations
        possible_paths = [
            user_home / ".EasyOCR" / "model",
            user_home / ".EasyOCR",
            Path.cwd() / ".EasyOCR" / "model",
        ]

        for model_dir in possible_paths:
            if model_dir.exists() and model_dir.is_dir():
                # Look for .pth files (PyTorch model files)
                for model_file in model_dir.rglob("*.pth"):
                    try:
                        with open(model_file, "rb") as f:
                            content = f.read()
                            sha256 = hashlib.sha256(content).hexdigest()
                            checksums[model_file.name] = sha256
                    except OSError:
                        pass  # Skip files we can't read

                # Also check for any other model-related files
                for model_file in model_dir.rglob("*"):
                    if model_file.is_file() and model_file.suffix in [".pth", ".pt", ".onnx"]:
                        try:
                            with open(model_file, "rb") as f:
                                content = f.read()
                                sha256 = hashlib.sha256(content).hexdigest()
                                checksums[model_file.name] = sha256
                        except OSError:
                            pass
    except Exception:
        pass  # If we can't find models, return empty dict

    return checksums


def capture_baseline(output_dir: Path) -> None:
    """Capture EasyOCR baseline outputs.

    Args:
        output_dir: Directory to write baseline.json and manifest.json.

    Raises:
        ImportError: If EasyOCR or PIL is not installed.
        RuntimeError: If capture fails.
    """
    if easyocr is None:
        msg = (
            "EasyOCR is not installed. Install it with: "
            "pip install -e '.[easyocr]'"
        )
        raise ImportError(msg)

    if Image is None:
        msg = "PIL (Pillow) is required. Install with: pip install -e '.[dev]'"
        raise ImportError(msg)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate synthetic fixtures
    fixtures = [
        ("Hello", 200, 50),
        ("World", 200, 50),
        ("EZRA", 200, 50),
        ("123", 150, 50),
    ]

    # Initialize plugin
    plugin = EasyOCRPlugin(device="cpu", languages=["en"])
    plugin.load("")  # EasyOCR loads models automatically

    # Run inference on all fixtures
    all_detections = []
    for text, width, height in fixtures:
        img = generate_synthetic_fixture(text, width, height)
        # Convert PIL Image to numpy array for EasyOCR
        import numpy as np

        img_array = np.array(img)
        result = plugin.infer(img_array)
        all_detections.extend(result["detections"])

    # Canonicalize output
    canonical_output = canonicalize_output({"detections": all_detections})

    # Write baseline.json
    baseline_path = output_dir / "baseline.json"
    with open(baseline_path, "w", encoding="utf-8") as f:
        f.write(to_canonical_json(canonical_output))

    # Collect manifest information
    try:
        import torch
        torch_version = torch.__version__
        torchvision_version = getattr(torch, "__version__", "unknown")
    except ImportError:
        torch_version = "not installed"
        torchvision_version = "not installed"

    # Try to get torchvision version separately
    try:
        import torchvision
        torchvision_version = torchvision.__version__
    except ImportError:
        pass

    model_checksums = get_model_checksums()

    manifest = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "easyocr_version": "1.7.2",
        "torch_version": torch_version,
        "torchvision_version": torchvision_version,
        "model_checksums": model_checksums,
        "fixture_set": "synthetic_basic",
        "device": "cpu",
    }

    # Write manifest.json
    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(to_canonical_json(manifest))

    print(f"Baseline captured to {output_dir}")
    print(f"   - baseline.json: {len(canonical_output['detections'])} detections")
    print(f"   - manifest.json: {len(model_checksums)} model files checksummed")


def main() -> None:
    """Main entry point for baseline capture tool."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Capture EasyOCR baseline outputs for regression testing"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("docs/baselines/easyocr/1.7.2/synthetic_basic"),
        help=(
            "Output directory for baseline artifacts "
            "(default: docs/baselines/easyocr/1.7.2/synthetic_basic)"
        ),
    )

    args = parser.parse_args()

    try:
        capture_baseline(args.output_dir)
    except Exception as e:
        print(f"Baseline capture failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

