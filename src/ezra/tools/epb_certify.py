"""EPB Consumer Certification — stdlib-only artifact validation.

Validates EPB v1.0.0 bundle structure, per-file hash integrity, and bundle hash
without importing any EZRA runtime code. Enables external consumers to verify
an EPB artifact in a trust-boundary-isolated way.

Allowed modules: argparse, hashlib, json, math, pathlib, sys only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

# EPB v1.0.0 canonicalization: 8 decimal places for non-zone files
EPB_FLOAT_PRECISION = 8
# Zone contract: 6 decimal places for zones.json
ZONE_FLOAT_PRECISION = 6

REQUIRED_FILES = ("manifest.json", "detections.json", "state.json", "hashes.json")
OPTIONAL_FILES = ("delta.json", "zones.json")


def _canonicalize_epb_value(obj: Any, float_precision: int = EPB_FLOAT_PRECISION) -> Any:
    """Recursively canonicalize a value for hashing (stdlib-only).

    Sorted keys, rounded floats, no NaN/Infinity.
    """
    if isinstance(obj, dict):
        return {k: _canonicalize_epb_value(v, float_precision) for k, v in sorted(obj.items())}
    if isinstance(obj, list):
        return [_canonicalize_epb_value(item, float_precision) for item in obj]
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            raise ValueError("NaN/Infinity not permitted in EPB bundles")
        return round(obj, float_precision)
    return obj


def _to_canonical_json(obj: Any, float_precision: int = EPB_FLOAT_PRECISION) -> str:
    """Produce canonical JSON string for hashing (matches EZRA emission)."""
    canonicalized = _canonicalize_epb_value(obj, float_precision)
    return json.dumps(
        canonicalized,
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    )


def _compute_file_hash(canonical_json: str) -> str:
    """SHA256 of UTF-8 encoded canonical JSON; lowercase hex."""
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def _compute_bundle_hash(file_hashes: dict[str, str]) -> str:
    """Bundle hash: exclude hashes.json, sort filenames, concat hashes, SHA256."""
    bundle_files = {k: v for k, v in file_hashes.items() if k != "hashes.json"}
    concatenated = "".join(bundle_files[name] for name in sorted(bundle_files.keys()))
    return hashlib.sha256(concatenated.encode("utf-8")).hexdigest()


def _check_structure(bundle_dir: Path) -> tuple[bool, list[str]]:
    """Verify required files exist and hashes.json has required keys. Returns (ok, errors)."""
    errors: list[str] = []
    for name in REQUIRED_FILES:
        if not (bundle_dir / name).is_file():
            errors.append(f"Missing required file: {name}")
    if errors:
        return False, errors

    try:
        hashes_content = (bundle_dir / "hashes.json").read_text(encoding="utf-8")
        hashes_dict = json.loads(hashes_content)
    except (OSError, json.JSONDecodeError) as e:
        return False, [f"Invalid hashes.json: {e}"]

    if "epb_version" not in hashes_dict:
        errors.append("hashes.json missing 'epb_version'")
    if "bundle_hash" not in hashes_dict:
        errors.append("hashes.json missing 'bundle_hash'")
    if "files" not in hashes_dict:
        errors.append("hashes.json missing 'files'")
    return len(errors) == 0, errors


def _verify_hash_integrity(bundle_dir: Path) -> tuple[bool, list[str]]:
    """Recompute per-file and bundle hashes from disk; compare to hashes.json."""
    errors: list[str] = []
    hashes_path = bundle_dir / "hashes.json"
    hashes_content = hashes_path.read_text(encoding="utf-8")
    hashes_dict = json.loads(hashes_content)
    files_map = hashes_dict["files"]
    declared_bundle_hash = hashes_dict["bundle_hash"]
    verified: dict[str, str] = {}
    hashes_json_declared: str | None = None

    for filename in sorted(files_map.keys()):
        declared = files_map[filename]
        if filename == "hashes.json":
            hashes_json_declared = declared
            continue

        path = bundle_dir / filename
        if not path.exists():
            errors.append(f"File declared in hashes.json missing on disk: {filename}")
            continue

        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            errors.append(f"{filename} invalid JSON: {e}")
            continue

        precision = ZONE_FLOAT_PRECISION if filename == "zones.json" else EPB_FLOAT_PRECISION
        try:
            canonical = _to_canonical_json(data, precision)
        except ValueError as e:
            errors.append(f"{filename} canonicalization: {e}")
            continue

        computed = _compute_file_hash(canonical)
        if computed != declared:
            errors.append(
                f"{filename} hash mismatch: declared {declared[:16]}..., "
                f"computed {computed[:16]}..."
            )
        else:
            verified[filename] = computed

    if errors:
        return False, errors

    computed_bundle = _compute_bundle_hash(verified)
    if computed_bundle != declared_bundle_hash:
        errors.append(
            f"bundle_hash mismatch: declared {declared_bundle_hash[:16]}..., "
            f"computed {computed_bundle[:16]}..."
        )
        return False, errors

    if hashes_json_declared is None:
        errors.append("hashes.json missing self-entry in files map")
        return False, errors

    hashes_without_self = {
        "epb_version": hashes_dict["epb_version"],
        "bundle_hash": declared_bundle_hash,
        "files": {k: v for k, v in files_map.items() if k != "hashes.json"},
    }
    computed_hashes_json = _compute_file_hash(_to_canonical_json(hashes_without_self))
    if computed_hashes_json != hashes_json_declared:
        errors.append("hashes.json self-hash mismatch")
        return False, errors

    return True, []


def certify(bundle_path: Path) -> dict[str, Any]:
    """Run full certification: structure and hash integrity.

    Returns a result dict with epb_version, structure_valid, hash_integrity_valid,
    bundle_hash_valid (same as hash_integrity for EPB v1), and valid (overall).
    """
    bundle_dir = Path(bundle_path).resolve()
    if not bundle_dir.is_dir():
        return {
            "valid": False,
            "epb_version": None,
            "structure_valid": False,
            "hash_integrity_valid": False,
            "bundle_hash_valid": False,
            "deterministic": False,
            "errors": [f"Not a directory: {bundle_dir}"],
        }

    result: dict[str, Any] = {
        "valid": True,
        "epb_version": "1.0.0",
        "structure_valid": True,
        "hash_integrity_valid": True,
        "bundle_hash_valid": True,
        "deterministic": True,
    }

    ok, errs = _check_structure(bundle_dir)
    if not ok:
        result["structure_valid"] = False
        result["valid"] = False
        result["deterministic"] = False
        result["errors"] = errs
        return result

    try:
        hashes_dict = json.loads((bundle_dir / "hashes.json").read_text(encoding="utf-8"))
        result["epb_version"] = hashes_dict.get("epb_version", "1.0.0")
    except (OSError, json.JSONDecodeError):
        pass

    ok2, errs2 = _verify_hash_integrity(bundle_dir)
    if not ok2:
        result["hash_integrity_valid"] = False
        result["bundle_hash_valid"] = False
        result["valid"] = False
        result["deterministic"] = False
        result["errors"] = result.get("errors", []) + errs2
        return result

    return result


def main() -> int:
    """Entry point: parse args, run certification, print JSON to stdout, exit 0/1."""
    parser = argparse.ArgumentParser(
        description="EPB Consumer Certification — validate EPB bundle (stdlib only)."
    )
    parser.add_argument(
        "bundle_path",
        type=Path,
        help="Path to EPB bundle directory",
    )
    args = parser.parse_args()
    out = certify(args.bundle_path)
    print(json.dumps(out, sort_keys=True))
    return 0 if out.get("valid", False) else 1


if __name__ == "__main__":
    sys.exit(main())
