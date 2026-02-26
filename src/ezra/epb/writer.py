"""EPB bundle writer for writing EPB directories to disk.

This module writes EPB v1.0.0 bundles to disk with deterministic
file ordering and LF line endings enforcement.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from ezra.epb.canonical import to_canonical_json
from ezra.epb.hash_verifier import verify_epb_bundle
from ezra.epb.hasher import build_hashes_dict, compute_file_hash
from ezra.epb.schema_validator import validate_bundle
from ezra.epb.zone_adapter import adapt_zone_registry_to_epb, to_zone_canonical_json
from ezra.zones.registry import ZoneRegistry


def write_epb_bundle(
    bundle: dict[str, Any],
    output_dir: Path,
    zone_registry: ZoneRegistry | None = None,
) -> None:
    """Write EPB v1.0.0 bundle to disk.

    Writes files in deterministic order:
    1. manifest.json
    2. detections.json
    3. state.json (if present)
    4. delta.json (if present)
    5. zones.json (if zone_registry provided)
    6. hashes.json (computed last)

    All files are written with:
    - Canonical JSON (sorted keys, 8dp floats for EPB files, 6dp for zones.json, indented 2-space)
    - LF line endings (enforced by canonical JSON + explicit LF write)
    - UTF-8 encoding

    Args:
        bundle: EPB bundle dictionary from build_epb_bundle().
        output_dir: Directory path to write EPB bundle to (created if needed).
        zone_registry: Optional zone registry to include as zones.json (must be frozen if provided).

    Raises:
        ValueError: If bundle fails JSON Schema validation or zone registry is not frozen.
        OSError: If directory creation or file writing fails.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Validate bundle against JSON Schemas before hashing/writing
    validate_bundle(bundle)

    # Compute file hashes (in deterministic order)
    manifest_hash = compute_file_hash(bundle["manifest"])
    detections_hash = compute_file_hash(bundle["detections"])
    state_hash = compute_file_hash(bundle["state"])  # Always present

    delta_hash: str | None = None
    if bundle["delta"] is not None:
        delta_hash = compute_file_hash(bundle["delta"])

    # Handle zones.json if zone_registry provided
    zones_hash: str | None = None
    if zone_registry is not None:
        # Adapt registry to EPB format
        zones_dict = adapt_zone_registry_to_epb(zone_registry)
        # Serialize with 6dp precision (zone contract)
        zones_json = to_zone_canonical_json(zones_dict)
        # Compute hash from JSON string (6dp precision)
        zones_hash = hashlib.sha256(zones_json.encode("utf-8")).hexdigest()

    # Write files in deterministic order
    # 1. manifest.json
    manifest_path = output_dir / "manifest.json"
    manifest_json = to_canonical_json(bundle["manifest"])
    manifest_path.write_text(manifest_json + "\n", encoding="utf-8", newline="")

    # 2. detections.json
    detections_path = output_dir / "detections.json"
    detections_json = to_canonical_json(bundle["detections"])
    detections_path.write_text(detections_json + "\n", encoding="utf-8", newline="")

    # 3. state.json (always present)
    state_path = output_dir / "state.json"
    state_json = to_canonical_json(bundle["state"])
    state_path.write_text(state_json + "\n", encoding="utf-8", newline="")

    # 4. delta.json (if present)
    if bundle["delta"] is not None:
        delta_path = output_dir / "delta.json"
        delta_json = to_canonical_json(bundle["delta"])
        delta_path.write_text(delta_json + "\n", encoding="utf-8", newline="")

    # 5. zones.json (if zone_registry provided)
    if zone_registry is not None:
        zones_path = output_dir / "zones.json"
        zones_path.write_text(zones_json + "\n", encoding="utf-8", newline="")

    # 6. hashes.json (computed last, after all other files)
    hashes_dict = build_hashes_dict(
        manifest_hash=manifest_hash,
        detections_hash=detections_hash,
        state_hash=state_hash,
        delta_hash=delta_hash,
        zones_hash=zones_hash,
    )
    hashes_path = output_dir / "hashes.json"
    hashes_json = to_canonical_json(hashes_dict)
    hashes_path.write_text(hashes_json + "\n", encoding="utf-8", newline="")

    # 7. Verify bundle integrity (recompute hashes from disk and compare)
    verify_epb_bundle(output_dir)
