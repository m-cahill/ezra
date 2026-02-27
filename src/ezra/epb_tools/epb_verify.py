"""EPB Artifact Verification — verify detached Ed25519 signature over bundle hash.

Recomputes the canonical bundle hash (stdlib-only via _epb_hash) and verifies
the signature in bundle.sig. Uses stdlib + cryptography only; no ezra.core or ezra.epb imports.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from ezra.tools._epb_hash import compute_bundle_hash

DEFAULT_SIG_FILENAME = "bundle.sig"


def verify_bundle(bundle_dir: Path, sig_path: Path) -> tuple[bool, str | None]:
    """Verify detached signature against bundle. Returns (valid, error_message)."""
    bundle_dir = Path(bundle_dir).resolve()
    sig_path = Path(sig_path).resolve()

    if not bundle_dir.is_dir():
        return False, f"Not a directory: {bundle_dir}"
    if not sig_path.is_file():
        return False, f"Signature file not found: {sig_path}"

    try:
        sig_content = sig_path.read_text(encoding="utf-8")
        sig_obj = json.loads(sig_content)
    except (OSError, json.JSONDecodeError) as e:
        return False, f"Invalid signature file: {e}"

    for key in ("algorithm", "bundle_hash", "signature", "public_key"):
        if key not in sig_obj:
            return False, f"Signature file missing '{key}'"
    if sig_obj.get("algorithm") != "ed25519":
        return False, f"Unsupported algorithm: {sig_obj.get('algorithm')}"

    try:
        computed_hash = compute_bundle_hash(bundle_dir)
    except ValueError as e:
        return False, str(e)

    if computed_hash != sig_obj["bundle_hash"]:
        return False, (
            f"Bundle hash mismatch: computed {computed_hash[:16]}..., "
            f"signed {sig_obj['bundle_hash'][:16]}..."
        )

    try:
        sig_bytes = base64.b64decode(sig_obj["signature"], validate=True)
        pub_bytes = base64.b64decode(sig_obj["public_key"], validate=True)
    except Exception as e:
        return False, f"Invalid base64 in signature file: {e}"

    try:
        public_key = Ed25519PublicKey.from_public_bytes(pub_bytes)
    except Exception as e:
        return False, f"Invalid public key: {e}"

    payload_bytes = bytes.fromhex(computed_hash)
    try:
        public_key.verify(sig_bytes, payload_bytes)
    except InvalidSignature:
        return False, "Signature verification failed"
    return True, None


def main() -> int:
    """Entry point: parse args, verify, print JSON result, exit 0/1."""
    parser = argparse.ArgumentParser(
        description="EPB Artifact Verification — verify detached Ed25519 signature."
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
        help=f"Path to signature file (default: <bundle_path>/{DEFAULT_SIG_FILENAME})",
    )
    args = parser.parse_args()

    bundle_dir = Path(args.bundle_path).resolve()
    sig_path = args.sig_path if args.sig_path is not None else bundle_dir / DEFAULT_SIG_FILENAME

    valid, error = verify_bundle(bundle_dir, sig_path)
    result: dict[str, bool | str] = {"valid": valid}
    if error is not None:
        result["error"] = error

    print(json.dumps(result, sort_keys=True))
    return 0 if valid else 1


if __name__ == "__main__":
    sys.exit(main())
