"""EPB Consumer Certification contract tests.

Validates that:
- EPB bundle hash integrity is verified by the stdlib-only certifier.
- Certification runs in isolation via subprocess
  (python -m ezra.epb_tools.epb_certify).
- Reproducibility: emit → rmtree → re-emit produces identical bundle hash.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from ezra.epb import build_epb_bundle, write_epb_bundle
from ezra.epb_tools.epb_certify import certify

FIXED_TIMESTAMP = datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)


def _make_bundle_dir(tmp_path: Path, subdir: str = "epb") -> Path:
    """Build and write a deterministic EPB bundle; return path to bundle dir."""
    bundle = build_epb_bundle(
        detections=[{"text": "Hello", "confidence": 0.9, "bbox": [10.0, 20.0, 50.0, 40.0]}],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 200, "height": 100, "channels": 3},
        timestamp=FIXED_TIMESTAMP,
    )
    out = tmp_path / subdir
    write_epb_bundle(bundle, out)
    return out


def test_epb_hash_integrity(tmp_path: Path) -> None:
    """Certifier reports hash_integrity_valid and bundle_hash_valid for valid bundle."""
    bundle_dir = _make_bundle_dir(tmp_path)
    result = certify(bundle_dir)
    assert result["valid"] is True
    assert result["hash_integrity_valid"] is True
    assert result["bundle_hash_valid"] is True
    assert result["structure_valid"] is True
    assert result.get("deterministic") is True


def test_epb_consumer_certification_subprocess(tmp_path: Path) -> None:
    """Certification runs via python -m ezra.epb_tools.epb_certify; exit 0 and JSON."""
    bundle_dir = _make_bundle_dir(tmp_path)
    proc = subprocess.run(
        [sys.executable, "-m", "ezra.epb_tools.epb_certify", str(bundle_dir)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert proc.returncode == 0, f"stderr: {proc.stderr}"
    out = json.loads(proc.stdout)
    assert out["valid"] is True
    assert out["structure_valid"] is True
    assert out["hash_integrity_valid"] is True
    assert out["bundle_hash_valid"] is True
    assert "epb_version" in out
    assert out["epb_version"] == "1.0.0"


def test_epb_reproducibility_clean_environment(tmp_path: Path) -> None:
    """Emit to a, rmtree a, emit to b; bundle hashes match (dir independence)."""
    bundle_dir_a = _make_bundle_dir(tmp_path, "a")
    hashes_a = json.loads((bundle_dir_a / "hashes.json").read_text(encoding="utf-8"))
    bundle_hash_a = hashes_a["bundle_hash"]

    shutil.rmtree(bundle_dir_a)

    bundle_dir_b = _make_bundle_dir(tmp_path, "b")
    hashes_b = json.loads((bundle_dir_b / "hashes.json").read_text(encoding="utf-8"))
    bundle_hash_b = hashes_b["bundle_hash"]

    assert bundle_hash_a == bundle_hash_b


def test_epb_certify_fails_on_tampered_bundle(tmp_path: Path) -> None:
    """Certifier reports invalid when a file is tampered after emission."""
    bundle_dir = _make_bundle_dir(tmp_path)
    manifest_path = bundle_dir / "manifest.json"
    content = manifest_path.read_text(encoding="utf-8")
    manifest_path.write_text(content.replace("1.0.0", "9.9.9"), encoding="utf-8")

    result = certify(bundle_dir)
    assert result["valid"] is False
    assert result["hash_integrity_valid"] is False


def test_epb_certify_fails_on_missing_file(tmp_path: Path) -> None:
    """Certifier reports invalid when a required file is missing."""
    bundle_dir = _make_bundle_dir(tmp_path)
    (bundle_dir / "manifest.json").unlink()

    result = certify(bundle_dir)
    assert result["valid"] is False
    assert result["structure_valid"] is False or result["hash_integrity_valid"] is False


def test_epb_certify_fails_on_invalid_path(tmp_path: Path) -> None:
    """Certifier reports invalid for non-directory path."""
    result = certify(tmp_path / "nonexistent")
    assert result["valid"] is False
    assert "errors" in result
