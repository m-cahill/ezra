"""EPB Certification Metadata — generate detached bundle.cert.json envelope.

Aggregates certification (structure, hash integrity, bundle hash) and
signature verification results into a canonical JSON envelope for
archival and compliance. Uses existing epb_certify and epb_verify;
does not hard-fail on missing signature.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ezra.tools.epb_certify import certify
from ezra.tools.epb_verify import DEFAULT_SIG_FILENAME, verify_bundle


def _get_certifier_version() -> str:
    """Certifier version: ezra.__version__, else package metadata, else 'unknown'."""
    try:
        from ezra import __version__
        return __version__
    except ImportError:
        pass
    try:
        from importlib.metadata import version
        return version("ezra")
    except Exception:
        pass
    return "unknown"


def _get_bundle_hash_and_epb_version(bundle_dir: Path) -> tuple[str | None, str]:
    """Read bundle_hash and epb_version from hashes.json when possible."""
    hashes_path = bundle_dir / "hashes.json"
    if not hashes_path.is_file():
        return None, "unknown"
    try:
        data = json.loads(hashes_path.read_text(encoding="utf-8"))
        return data.get("bundle_hash"), data.get("epb_version", "unknown")
    except (OSError, json.JSONDecodeError):
        return None, "unknown"


def generate_cert_metadata(bundle_path: Path) -> dict[str, Any]:
    """Build certification metadata envelope for an EPB bundle directory.

    Runs certification and optional signature verification; never
    hard-fails on missing signature. Returns the envelope dict
    (nested shape).
    """
    bundle_dir = Path(bundle_path).resolve()
    cert_result = certify(bundle_dir)

    bundle_hash, epb_version = _get_bundle_hash_and_epb_version(bundle_dir)
    if cert_result.get("epb_version"):
        epb_version = cert_result["epb_version"]
    if bundle_hash is None and cert_result.get("valid"):
        hashes_path = bundle_dir / "hashes.json"
        if hashes_path.is_file():
            try:
                data = json.loads(hashes_path.read_text(encoding="utf-8"))
                bundle_hash = data.get("bundle_hash")
            except (OSError, json.JSONDecodeError):
                pass

    sig_path = bundle_dir / DEFAULT_SIG_FILENAME
    sig_present = sig_path.is_file()
    sig_valid = False
    sig_algorithm: str | None = "ed25519" if sig_present else None
    if sig_present:
        valid, _ = verify_bundle(bundle_dir, sig_path)
        sig_valid = valid

    env: dict[str, Any] = {
        "certification": {
            "bundle_hash_valid": cert_result.get("bundle_hash_valid", False),
            "hash_integrity_valid": cert_result.get("hash_integrity_valid", False),
            "structure_valid": cert_result.get("structure_valid", False),
        },
        "environment": {
            "certifier_version": _get_certifier_version(),
            "python_version": (
                f"{sys.version_info.major}.{sys.version_info.minor}"
                f".{sys.version_info.micro}"
            ),
        },
        "epb_version": epb_version,
        "bundle_hash": bundle_hash or "",
        "generated_at_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "signature": {
            "algorithm": sig_algorithm,
            "present": sig_present,
            "valid": sig_valid,
        },
    }
    return env


def write_canonical_cert_json(envelope: dict[str, Any], out_path: Path) -> None:
    """Write envelope as canonical JSON (sorted keys, UTF-8, LF)."""
    json_str = json.dumps(
        envelope,
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    )
    out_path.write_text(json_str + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    """Entry point: generate bundle.cert.json; exit 0 if cert valid else 1."""
    parser = argparse.ArgumentParser(
        description="EPB Certification Metadata — generate detached bundle.cert.json envelope."
    )
    parser.add_argument(
        "bundle_path",
        type=Path,
        help="Path to EPB bundle directory",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output path (default: <bundle_path>/bundle.cert.json)",
    )
    args = parser.parse_args()

    bundle_dir = Path(args.bundle_path).resolve()
    if not bundle_dir.is_dir():
        print(f"Error: Not a directory: {bundle_dir}", file=sys.stderr)
        return 1

    envelope = generate_cert_metadata(bundle_dir)
    out_path = (
        args.output if args.output is not None else bundle_dir / "bundle.cert.json"
    )
    write_canonical_cert_json(envelope, out_path)

    cert_valid = (
        envelope["certification"]["structure_valid"]
        and envelope["certification"]["hash_integrity_valid"]
        and envelope["certification"]["bundle_hash_valid"]
    )
    return 0 if cert_valid else 1


if __name__ == "__main__":
    sys.exit(main())
