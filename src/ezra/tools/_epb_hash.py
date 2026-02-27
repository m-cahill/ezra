"""Stdlib-only EPB bundle hash computation for signing/verification.

Used by epb_sign.py and epb_verify.py to compute the canonical bundle hash
without importing ezra.core or ezra.epb. Matches EPB v1.0.0 canonicalization.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

# EPB v1.0.0 canonicalization
EPB_FLOAT_PRECISION = 8
ZONE_FLOAT_PRECISION = 6

REQUIRED_FILES = ("manifest.json", "detections.json", "state.json", "hashes.json")
OPTIONAL_FILES = ("delta.json", "zones.json")


def _canonicalize_epb_value(obj: Any, float_precision: int = EPB_FLOAT_PRECISION) -> Any:
    """Recursively canonicalize a value for hashing (sorted keys, rounded floats)."""
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
    """Produce canonical JSON string for hashing."""
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


def _compute_bundle_hash_from_file_hashes(file_hashes: dict[str, str]) -> str:
    """Bundle hash: exclude hashes.json, sort filenames, concat hashes, SHA256."""
    bundle_files = {k: v for k, v in file_hashes.items() if k != "hashes.json"}
    concatenated = "".join(bundle_files[name] for name in sorted(bundle_files.keys()))
    return hashlib.sha256(concatenated.encode("utf-8")).hexdigest()


def compute_bundle_hash(bundle_dir: Path) -> str:
    """Compute canonical bundle hash from bundle directory (stdlib-only).

    Reads and canonicalizes each file per EPB v1.0.0 rules, then returns
    the bundle hash (SHA256 of concatenated file hashes, excluding hashes.json).

    Raises:
        ValueError: If structure is invalid or hash integrity fails.
    """
    bundle_dir = Path(bundle_dir).resolve()
    if not bundle_dir.is_dir():
        raise ValueError(f"Not a directory: {bundle_dir}")

    for name in REQUIRED_FILES:
        if not (bundle_dir / name).is_file():
            raise ValueError(f"Missing required file: {name}")

    hashes_path = bundle_dir / "hashes.json"
    try:
        hashes_dict = json.loads(hashes_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise ValueError(f"Invalid hashes.json: {e}") from e

    files_map = hashes_dict.get("files")
    if not files_map:
        raise ValueError("hashes.json missing 'files'")

    verified: dict[str, str] = {}
    for filename in sorted(files_map.keys()):
        if filename == "hashes.json":
            continue
        path = bundle_dir / filename
        if not path.exists():
            raise ValueError(f"File declared in hashes.json missing on disk: {filename}")
        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"{filename} invalid JSON: {e}") from e
        precision = ZONE_FLOAT_PRECISION if filename == "zones.json" else EPB_FLOAT_PRECISION
        try:
            canonical = _to_canonical_json(data, precision)
        except ValueError as e:
            raise ValueError(f"{filename} canonicalization: {e}") from e
        computed = _compute_file_hash(canonical)
        if computed != files_map[filename]:
            raise ValueError(
                f"{filename} hash mismatch: declared {files_map[filename][:16]}..., "
                f"computed {computed[:16]}..."
            )
        verified[filename] = computed

    return _compute_bundle_hash_from_file_hashes(verified)
