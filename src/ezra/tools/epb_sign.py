"""EPB Artifact Signing — detached Ed25519 signature over bundle hash.

Computes the canonical bundle hash (stdlib-only via _epb_hash) and signs it with
Ed25519. Outputs bundle.sig (JSON) with algorithm, bundle_hash, signature, public_key.
Uses stdlib + cryptography only; no ezra.core or ezra.epb imports.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from ezra.tools._epb_hash import compute_bundle_hash

SIG_ALGORITHM = "ed25519"
DEFAULT_SIG_FILENAME = "bundle.sig"


def _sign_payload(private_key: Ed25519PrivateKey, payload_hex: str) -> tuple[bytes, bytes]:
    """Sign payload (hex string) and return (signature_bytes, public_key_bytes)."""
    payload_bytes = bytes.fromhex(payload_hex)
    signature = private_key.sign(payload_bytes)
    public_key = private_key.public_key()
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return signature, public_key_bytes


def sign_bundle(
    bundle_dir: Path,
    sig_path: Path,
    signing_key: Ed25519PrivateKey | None = None,
) -> dict[str, str]:
    """Compute bundle hash, sign it, write sig_path. Return sig dict (for tests/stdout).

    If signing_key is None, generates an ephemeral key. Does not persist private key.
    """
    bundle_dir = Path(bundle_dir).resolve()
    bundle_hash = compute_bundle_hash(bundle_dir)

    if signing_key is None:
        signing_key = Ed25519PrivateKey.generate()

    signature_bytes, public_key_bytes = _sign_payload(signing_key, bundle_hash)

    sig_obj = {
        "algorithm": SIG_ALGORITHM,
        "bundle_hash": bundle_hash,
        "signature": base64.b64encode(signature_bytes).decode("ascii"),
        "public_key": base64.b64encode(public_key_bytes).decode("ascii"),
    }

    sig_path = Path(sig_path).resolve()
    sig_path.write_text(json.dumps(sig_obj, sort_keys=True, indent=2), encoding="utf-8")

    return sig_obj


def main() -> int:
    """Entry point: parse args, sign bundle, print public key / JSON, exit 0/1."""
    parser = argparse.ArgumentParser(
        description="EPB Artifact Signing — sign bundle hash with Ed25519 (detached)."
    )
    parser.add_argument(
        "bundle_path",
        type=Path,
        help="Path to EPB bundle directory",
    )
    parser.add_argument(
        "--sig-path",
        type=Path,
        default=None,
        help=f"Output signature file path (default: <bundle_path>/{DEFAULT_SIG_FILENAME})",
    )
    parser.add_argument(
        "--private-key",
        type=Path,
        default=None,
        help="Path to PEM-encoded Ed25519 private key (default: generate ephemeral)",
    )
    parser.add_argument(
        "--public-key-out",
        type=Path,
        default=None,
        help="Optional path to write PEM public key",
    )
    args = parser.parse_args()

    bundle_dir = Path(args.bundle_path).resolve()
    if not bundle_dir.is_dir():
        err_msg = json.dumps({"error": f"Not a directory: {bundle_dir}"}, sort_keys=True)
        print(err_msg, file=sys.stderr)
        return 1

    sig_path = args.sig_path
    if sig_path is None:
        sig_path = bundle_dir / DEFAULT_SIG_FILENAME

    signing_key: Ed25519PrivateKey | None = None
    if args.private_key is not None:
        pem = Path(args.private_key).read_text(encoding="utf-8")
        loaded = serialization.load_pem_private_key(
            pem.encode("utf-8"),
            password=None,
        )
        if not isinstance(loaded, Ed25519PrivateKey):
            print(
                json.dumps({"error": "Private key must be Ed25519"}, sort_keys=True),
                file=sys.stderr,
            )
            return 1
        signing_key = loaded

    try:
        sig_obj = sign_bundle(bundle_dir, sig_path, signing_key=signing_key)
    except ValueError as e:
        print(json.dumps({"error": str(e)}, sort_keys=True), file=sys.stderr)
        return 1

    if args.public_key_out is not None:
        pub_b64 = sig_obj["public_key"]
        pub_bytes = base64.b64decode(pub_b64)
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        pub_key = Ed25519PublicKey.from_public_bytes(pub_bytes)
        pem = pub_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")
        Path(args.public_key_out).write_text(pem, encoding="utf-8")

    # Print public key (base64) for ephemeral case / scripting
    print(
        json.dumps(
            {"public_key": sig_obj["public_key"], "bundle_hash": sig_obj["bundle_hash"]},
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
