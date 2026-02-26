"""SHA256 hashing for EPB v1.0.0 bundles.

This module computes deterministic SHA256 hashes per EPB spec:
- Per-file hashes of canonical JSON strings
- Bundle hash from sorted file hash concatenation (excluding hashes.json)
"""

from __future__ import annotations

import hashlib
from typing import Any

from ezra.epb.canonical import to_canonical_json


def compute_file_hash(content: dict[str, Any]) -> str:
    """Compute SHA256 hash of canonical JSON content.

    Args:
        content: Dictionary to hash (will be canonicalized).

    Returns:
        Lowercase hexadecimal SHA256 hash (64 characters).
    """
    canonical_json = to_canonical_json(content)
    sha256 = hashlib.sha256(canonical_json.encode("utf-8"))
    return sha256.hexdigest()


def compute_bundle_hash(file_hashes: dict[str, str]) -> str:
    """Compute bundle hash from sorted file hashes.

    Per EPB v1.0.0 spec Section 4.3:
    - Sort file names alphabetically
    - Concatenate file hashes in sorted order
    - Compute SHA256 of concatenated string
    - Exclude hashes.json from bundle hash computation

    Args:
        file_hashes: Dictionary mapping filename -> SHA256 hash.
                    Must NOT include hashes.json in the bundle hash computation.

    Returns:
        Lowercase hexadecimal SHA256 bundle hash (64 characters).
    """
    # Exclude hashes.json from bundle hash computation (per spec)
    bundle_files = {k: v for k, v in file_hashes.items() if k != "hashes.json"}

    # Sort file names alphabetically
    sorted_names = sorted(bundle_files.keys())

    # Concatenate file hashes in sorted order
    concatenated = "".join(bundle_files[name] for name in sorted_names)

    # Compute SHA256 of concatenated string
    sha256 = hashlib.sha256(concatenated.encode("utf-8"))
    return sha256.hexdigest()


def build_hashes_dict(
    manifest_hash: str,
    detections_hash: str,
    state_hash: str,
    delta_hash: str | None = None,
    zones_hash: str | None = None,
) -> dict[str, Any]:
    """Build hashes.json structure.

    Args:
        manifest_hash: SHA256 hash of manifest.json.
        detections_hash: SHA256 hash of detections.json.
        state_hash: SHA256 hash of state.json (required).
        delta_hash: SHA256 hash of delta.json (or None if absent).
        zones_hash: SHA256 hash of zones.json (or None if absent).

    Returns:
        Dictionary containing hashes.json structure with bundle_hash computed.
    """
    # Build files map (excluding hashes.json from bundle hash computation)
    files: dict[str, str] = {
        "detections.json": detections_hash,
        "manifest.json": manifest_hash,
        "state.json": state_hash,
    }

    # Add delta.json only if present
    if delta_hash is not None:
        files["delta.json"] = delta_hash

    # Add zones.json only if present
    if zones_hash is not None:
        files["zones.json"] = zones_hash

    # Compute bundle hash (excluding hashes.json)
    bundle_hash = compute_bundle_hash(files)

    # Build hashes.json structure (without hashes.json entry in files map yet)
    hashes_dict: dict[str, Any] = {
        "epb_version": "1.0.0",
        "bundle_hash": bundle_hash,
        "files": {
            "detections.json": detections_hash,
            "manifest.json": manifest_hash,
            "state.json": state_hash,
        },
    }

    if delta_hash is not None:
        hashes_dict["files"]["delta.json"] = delta_hash

    if zones_hash is not None:
        hashes_dict["files"]["zones.json"] = zones_hash

    # Compute hashes.json hash (from structure without its own entry)
    hashes_json_hash = compute_file_hash(hashes_dict)

    # Add hashes.json to files map (required by schema, but excluded from bundle_hash)
    hashes_dict["files"]["hashes.json"] = hashes_json_hash

    return hashes_dict
