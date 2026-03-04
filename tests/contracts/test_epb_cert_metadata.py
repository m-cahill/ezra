"""EPB Certification Metadata contract tests.

Validates that:
- Valid bundle produces well-formed bundle.cert.json with correct nested shape.
- Tampered payload or hashes.json produces certification invalid in metadata.
- Tampered bundle.sig produces signature.present true, signature.valid false.
- Bundle without signature produces present false, valid false; no hard-fail.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from ezra.epb_tools.epb_generate_cert_metadata import generate_cert_metadata
from ezra.tools.epb_sign import sign_bundle

from .test_epb_consumer_certification import _make_bundle_dir


def test_metadata_valid_structure(tmp_path: Path) -> None:
    """Valid bundle yields envelope with nested shape and all cert true."""
    bundle_dir = _make_bundle_dir(tmp_path, "epb")

    envelope = generate_cert_metadata(bundle_dir)

    assert "epb_version" in envelope
    assert envelope["epb_version"] == "1.0.0"
    assert "bundle_hash" in envelope
    assert len(envelope["bundle_hash"]) == 64
    assert envelope["certification"]["structure_valid"] is True
    assert envelope["certification"]["hash_integrity_valid"] is True
    assert envelope["certification"]["bundle_hash_valid"] is True
    assert "signature" in envelope
    assert "environment" in envelope
    assert "generated_at_utc" in envelope
    assert "python_version" in envelope["environment"]
    assert "certifier_version" in envelope["environment"]


def test_metadata_no_signature_case(tmp_path: Path) -> None:
    """Bundle without bundle.sig: present false, valid false; certification still valid."""
    bundle_dir = _make_bundle_dir(tmp_path, "epb")
    assert not (bundle_dir / "bundle.sig").exists()

    envelope = generate_cert_metadata(bundle_dir)

    assert envelope["signature"]["present"] is False
    assert envelope["signature"]["valid"] is False
    assert envelope["signature"]["algorithm"] is None
    assert envelope["certification"]["structure_valid"] is True
    assert envelope["certification"]["hash_integrity_valid"] is True
    assert envelope["certification"]["bundle_hash_valid"] is True


def test_metadata_with_signature_valid(tmp_path: Path) -> None:
    """Signed bundle: present true, valid true, algorithm ed25519."""
    bundle_dir = _make_bundle_dir(tmp_path, "epb")
    sign_bundle(bundle_dir, bundle_dir / "bundle.sig", signer=None)

    envelope = generate_cert_metadata(bundle_dir)

    assert envelope["signature"]["present"] is True
    assert envelope["signature"]["valid"] is True
    assert envelope["signature"]["algorithm"] == "ed25519"


def test_metadata_invalid_if_tampered_payload(tmp_path: Path) -> None:
    """Tamper state.json: hash_integrity_valid and bundle_hash_valid false."""
    bundle_dir = _make_bundle_dir(tmp_path, "epb")
    state_path = bundle_dir / "state.json"
    content = state_path.read_text(encoding="utf-8")
    state_path.write_text(content.replace("1.0.0", "9.9.9"), encoding="utf-8")

    envelope = generate_cert_metadata(bundle_dir)

    assert envelope["certification"]["hash_integrity_valid"] is False
    assert envelope["certification"]["bundle_hash_valid"] is False
    assert envelope["certification"]["structure_valid"] is True


def test_metadata_invalid_if_hashes_json_tampered(tmp_path: Path) -> None:
    """Tamper hashes.json only: hash_integrity_valid and bundle_hash_valid false."""
    bundle_dir = _make_bundle_dir(tmp_path, "epb")
    hashes_path = bundle_dir / "hashes.json"
    data = json.loads(hashes_path.read_text(encoding="utf-8"))
    data["bundle_hash"] = "a" * 64
    hashes_path.write_text(
        json.dumps(data, sort_keys=True, indent=2),
        encoding="utf-8",
    )

    envelope = generate_cert_metadata(bundle_dir)

    assert envelope["certification"]["hash_integrity_valid"] is False
    assert envelope["certification"]["bundle_hash_valid"] is False


def test_metadata_signature_present_but_invalid(tmp_path: Path) -> None:
    """Tamper bundle.sig: present true, valid false."""
    bundle_dir = _make_bundle_dir(tmp_path, "epb")
    sign_bundle(bundle_dir, bundle_dir / "bundle.sig", signer=None)
    sig_path = bundle_dir / "bundle.sig"
    sig_data = json.loads(sig_path.read_text(encoding="utf-8"))
    sig_data["signature"] = "X" * 44
    sig_path.write_text(
        json.dumps(sig_data, sort_keys=True, indent=2),
        encoding="utf-8",
    )

    envelope = generate_cert_metadata(bundle_dir)

    assert envelope["signature"]["present"] is True
    assert envelope["signature"]["valid"] is False
    assert envelope["signature"]["algorithm"] == "ed25519"


def test_metadata_subprocess_exit_zero_when_valid(tmp_path: Path) -> None:
    """python -m ezra.epb_tools.epb_generate_cert_metadata exits 0 for valid bundle."""
    bundle_dir = _make_bundle_dir(tmp_path, "epb")
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "ezra.epb_tools.epb_generate_cert_metadata",
            str(bundle_dir),
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert proc.returncode == 0, proc.stderr
    assert (bundle_dir / "bundle.cert.json").is_file()
    cert = json.loads((bundle_dir / "bundle.cert.json").read_text(encoding="utf-8"))
    assert cert["certification"]["structure_valid"] is True
    assert cert["certification"]["hash_integrity_valid"] is True


def test_metadata_subprocess_exit_one_when_tampered(tmp_path: Path) -> None:
    """python -m ezra.epb_tools.epb_generate_cert_metadata exits 1 when cert invalid."""
    bundle_dir = _make_bundle_dir(tmp_path, "epb")
    (bundle_dir / "state.json").write_text('{"x": 1}', encoding="utf-8")

    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "ezra.epb_tools.epb_generate_cert_metadata",
            str(bundle_dir),
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert proc.returncode == 1
    assert (bundle_dir / "bundle.cert.json").is_file()
