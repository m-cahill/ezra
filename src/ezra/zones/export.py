"""Zone schema JSON export for contract locking.

This module exports zone registries to deterministic JSON files
for contract locking and cross-repo consumption.

This module handles file I/O concerns and delegates canonical serialization
to serialize.py for byte-level determinism.
"""

from __future__ import annotations

from pathlib import Path

from ezra.zones.registry import ZoneRegistry
from ezra.zones.serialize import serialize_zone_registry_pretty


def export_zone_schema_json(registry: ZoneRegistry, output_path: Path) -> None:
    """Export registry to deterministic JSON file.

    Args:
        registry: Zone registry to export.
        output_path: Path to write JSON file (created if needed).

    Raises:
        OSError: If file writing fails.

    Note:
        This function delegates to serialize.serialize_zone_registry_pretty()
        for canonical serialization. File I/O (path creation, encoding, line
        endings) is handled here.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Delegate to serialize module for canonical JSON formatting
    json_str = serialize_zone_registry_pretty(registry)

    # Write with LF line endings (consistent with EPB canonicalization)
    output_path.write_text(json_str, encoding="utf-8", newline="")
