"""EPB Artifact Signing contract tests.

Validates that:
- Sign + verify round-trip succeeds (ephemeral key).
- Tampered bundle fails verification.
- Wrong public key in sig file fails verification.
"""

from __future__ import annotations

import base64
import json
import subprocess
import sys
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from ezra.tools.epb_sign import sign_bundle
from ezra.tools.epb_verify import verify_bundle

from .test_epb_consumer_certification import _make_bundle_dir


def test_epb_sign_verify_roundtrip(tmp_path: Path) -> None:
    """Emit EPB, sign with ephemeral key, verify -> PASS."""
    bundle_dir = _make_bundle_dir(tmp_path, "epb")
    sig_path = bundle_dir / "bundle.sig"

    result = sign_bundle(bundle_dir, sig_path, signer=None)
    assert sig_path.is_file()
    assert result["algorithm"] == "ed25519"
    assert "bundle_hash" in result
    assert "signature" in result
    assert "public_key" in result

    valid, error = verify_bundle(bundle_dir, sig_path)
    assert valid is True, error
    assert error is None


def test_epb_sign_verify_subprocess(tmp_path: Path) -> None:
    """Sign and verify via python -m ezra.tools.epb_sign / epb_verify; exit 0."""
    bundle_dir = _make_bundle_dir(tmp_path, "epb")

    sign_proc = subprocess.run(
        [sys.executable, "-m", "ezra.tools.epb_sign", str(bundle_dir)],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(tmp_path),
    )
    assert sign_proc.returncode == 0, f"epb_sign stderr: {sign_proc.stderr}"
    assert (bundle_dir / "bundle.sig").is_file()
    sign_out = json.loads(sign_proc.stdout)
    assert "public_key" in sign_out
    assert "bundle_hash" in sign_out

    verify_proc = subprocess.run(
        [sys.executable, "-m", "ezra.tools.epb_verify", str(bundle_dir)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert verify_proc.returncode == 0, f"epb_verify stderr: {verify_proc.stderr}"
    verify_out = json.loads(verify_proc.stdout)
    assert verify_out["valid"] is True


def test_epb_verify_fails_on_tampered_bundle(tmp_path: Path) -> None:
    """Sign bundle, tamper a file, verify -> FAIL."""
    bundle_dir = _make_bundle_dir(tmp_path, "epb")
    sig_path = bundle_dir / "bundle.sig"
    sign_bundle(bundle_dir, sig_path, signer=None)

    # Tamper
    manifest_path = bundle_dir / "manifest.json"
    content = manifest_path.read_text(encoding="utf-8")
    manifest_path.write_text(content.replace("1.0.0", "9.9.9"), encoding="utf-8")

    valid, error = verify_bundle(bundle_dir, sig_path)
    assert valid is False
    assert error is not None
    assert "mismatch" in error.lower() or "failed" in error.lower()


def test_epb_verify_fails_wrong_public_key(tmp_path: Path) -> None:
    """Sig file has correct bundle_hash and signature from A, but public_key from B -> FAIL."""
    bundle_dir = _make_bundle_dir(tmp_path, "epb")
    sig_path = bundle_dir / "bundle.sig"

    key_a = Ed25519PrivateKey.generate()
    sign_bundle(bundle_dir, sig_path, signer=key_a)

    sig_obj = json.loads(sig_path.read_text(encoding="utf-8"))
    signature_from_a = sig_obj["signature"]
    bundle_hash = sig_obj["bundle_hash"]

    key_b = Ed25519PrivateKey.generate()
    pub_b = key_b.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    pub_b_b64 = base64.b64encode(pub_b).decode("ascii")

    # Replace public_key with B's; keep A's signature and bundle_hash
    tampered_sig = {
        "algorithm": "ed25519",
        "bundle_hash": bundle_hash,
        "signature": signature_from_a,
        "public_key": pub_b_b64,
    }
    sig_path.write_text(json.dumps(tampered_sig, sort_keys=True, indent=2), encoding="utf-8")

    valid, error = verify_bundle(bundle_dir, sig_path)
    assert valid is False
    assert error is not None
    assert "verification failed" in error or "Invalid" in error


def test_epb_sign_with_provided_private_key(tmp_path: Path) -> None:
    """Sign with --private-key (PEM file); verify passes."""
    bundle_dir = _make_bundle_dir(tmp_path, "epb")
    sig_path = bundle_dir / "bundle.sig"
    key_path = tmp_path / "key.pem"

    key = Ed25519PrivateKey.generate()
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    key_path.write_bytes(pem)

    sign_bundle(bundle_dir, sig_path, signer=key)
    assert sig_path.is_file()

    valid, _ = verify_bundle(bundle_dir, sig_path)
    assert valid is True


def test_epb_sign_fails_invalid_bundle(tmp_path: Path) -> None:
    """Sign on non-directory or invalid bundle -> error."""
    import pytest

    not_dir = tmp_path / "missing"
    sig_path = tmp_path / "out.sig"
    with pytest.raises(ValueError, match="Not a directory"):
        sign_bundle(not_dir, sig_path, signer=None)
