"""EPB bundle writer for writing EPB directories to disk.

This module writes EPB v1.0.0 bundles to disk with deterministic
file ordering and LF line endings enforcement.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ezra.epb.canonical import to_canonical_json
from ezra.epb.hasher import build_hashes_dict, compute_file_hash
from ezra.epb.schema_validator import validate_bundle


def write_epb_bundle(bundle: dict[str, Any], output_dir: Path) -> None:
    """Write EPB v1.0.0 bundle to disk.

    Writes files in deterministic order:
    1. manifest.json
    2. detections.json
    3. state.json (if present)
    4. delta.json (if present)
    5. hashes.json (computed last)

    All files are written with:
    - Canonical JSON (sorted keys, 8dp floats, indented 2-space)
    - LF line endings (enforced by to_canonical_json + explicit LF write)
    - UTF-8 encoding

    Args:
        bundle: EPB bundle dictionary from build_epb_bundle().
        output_dir: Directory path to write EPB bundle to (created if needed).

    Raises:
        ValueError: If bundle fails JSON Schema validation.
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

    # 5. hashes.json (computed last, after all other files)
    hashes_dict = build_hashes_dict(
        manifest_hash=manifest_hash,
        detections_hash=detections_hash,
        state_hash=state_hash,
        delta_hash=delta_hash,
    )
    hashes_path = output_dir / "hashes.json"
    hashes_json = to_canonical_json(hashes_dict)
    hashes_path.write_text(hashes_json + "\n", encoding="utf-8", newline="")
