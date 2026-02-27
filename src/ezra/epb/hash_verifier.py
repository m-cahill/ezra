"""EPB bundle hash integrity verification.

This module verifies that on-disk EPB bundle files match their declared
hashes in hashes.json. Verification recomputes SHA256 hashes from disk
content and compares against hashes.json entries.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ezra.epb.hasher import compute_bundle_hash, compute_file_hash
from ezra.epb.zone_adapter import to_zone_canonical_json
from ezra.errors import EPBHashError


def verify_epb_bundle(bundle_dir: Path) -> None:
    """Verify EPB bundle hash integrity.

    Recomputes SHA256 hashes of all bundle JSON files from disk content
    and verifies against hashes.json. Raises ValueError on mismatch.

    Verification rules:
    - Every file listed in hashes.json.files must exist on disk and match hash
    - hashes.json self-hash is verified (computed before self-entry is added)
    - bundle_hash is recomputed and verified
    - Extra on-disk files not in hashes.json.files are ignored

    Args:
        bundle_dir: Path to EPB bundle directory.

    Raises:
        EPBHashError: If any file hash mismatch, missing file, or bundle_hash mismatch.
        FileNotFoundError: If hashes.json is missing.
        json.JSONDecodeError: If hashes.json is invalid JSON.
    """
    bundle_dir = Path(bundle_dir)

    # Load hashes.json
    hashes_path = bundle_dir / "hashes.json"
    if not hashes_path.exists():
        raise EPBHashError(f"EPB bundle missing hashes.json: {hashes_path}")

    try:
        hashes_content = hashes_path.read_text(encoding="utf-8")
        hashes_dict = json.loads(hashes_content)
    except json.JSONDecodeError as e:
        raise EPBHashError(f"EPB bundle hashes.json is invalid JSON: {e}") from e

    # Validate hashes.json structure
    if "files" not in hashes_dict:
        raise EPBHashError("EPB bundle hashes.json missing 'files' field")
    if "bundle_hash" not in hashes_dict:
        raise EPBHashError("EPB bundle hashes.json missing 'bundle_hash' field")

    files_map = hashes_dict["files"]
    declared_bundle_hash = hashes_dict["bundle_hash"]

    # Verify each file listed in hashes.json.files (except hashes.json itself)
    verified_file_hashes: dict[str, str] = {}
    hashes_json_declared_hash: str | None = None

    for filename, declared_hash in files_map.items():
        if filename == "hashes.json":
            # Store for later verification (self-hash)
            hashes_json_declared_hash = declared_hash
            continue

        # Verify file exists
        file_path = bundle_dir / filename
        if not file_path.exists():
            raise EPBHashError(
                f"EPB bundle file declared in hashes.json but missing on disk: {filename}"
            )

        # Read file content and compute hash
        try:
            file_content = file_path.read_text(encoding="utf-8")
            # Parse JSON to canonicalize (same as emission)
            file_dict = json.loads(file_content)
            # zones.json uses 6dp precision (zone contract), not 8dp (EPB canonical)
            if filename == "zones.json":
                # Use zone canonicalization (6dp) for zones.json
                zones_json = to_zone_canonical_json(file_dict)
                computed_hash = hashlib.sha256(zones_json.encode("utf-8")).hexdigest()
            else:
                # Use EPB canonicalization (8dp) for all other files
                computed_hash = compute_file_hash(file_dict)
        except json.JSONDecodeError as e:
            raise EPBHashError(f"EPB bundle file {filename} is invalid JSON: {e}") from e

        # Compare hashes
        if computed_hash != declared_hash:
            raise EPBHashError(
                f"EPB bundle file {filename} hash mismatch:\n"
                f"  Declared: {declared_hash}\n"
                f"  Computed: {computed_hash}"
            )

        verified_file_hashes[filename] = computed_hash

    # Verify bundle_hash first (independent of self-hash)
    # Bundle hash is computed from all files EXCEPT hashes.json
    computed_bundle_hash = compute_bundle_hash(verified_file_hashes)

    if computed_bundle_hash != declared_bundle_hash:
        raise EPBHashError(
            f"EPB bundle bundle_hash mismatch:\n"
            f"  Declared: {declared_bundle_hash}\n"
            f"  Computed: {computed_bundle_hash}"
        )

    # Verify hashes.json self-hash (depends on bundle_hash being correct)
    if hashes_json_declared_hash is None:
        raise EPBHashError("EPB bundle hashes.json missing self-hash entry in files map")

    # Reconstruct hashes.json structure without self-entry (same as emission logic)
    # This matches the logic in build_hashes_dict() where self-hash is computed
    # before the self-entry is added
    hashes_dict_without_self = {
        "epb_version": hashes_dict["epb_version"],
        "bundle_hash": declared_bundle_hash,
        "files": {k: v for k, v in files_map.items() if k != "hashes.json"},
    }
    computed_hashes_json_hash = compute_file_hash(hashes_dict_without_self)

    if computed_hashes_json_hash != hashes_json_declared_hash:
        raise EPBHashError(
            f"EPB bundle hashes.json self-hash mismatch:\n"
            f"  Declared: {hashes_json_declared_hash}\n"
            f"  Computed: {computed_hashes_json_hash}"
        )
