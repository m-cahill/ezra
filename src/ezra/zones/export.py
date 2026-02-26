"""Zone schema JSON export for contract locking.

This module exports zone registries to deterministic JSON files
for contract locking and cross-repo consumption.
"""

from __future__ import annotations

import json
from pathlib import Path

from ezra.zones.registry import ZoneRegistry


def export_zone_schema_json(registry: ZoneRegistry, output_path: Path) -> None:
    """Export registry to deterministic JSON file.

    Args:
        registry: Zone registry to export.
        output_path: Path to write JSON file (created if needed).

    Raises:
        OSError: If file writing fails.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Export to dict (already deterministic)
    data = registry.export_to_dict()

    # Serialize to JSON with deterministic formatting
    # Use sort_keys=True for additional stability
    json_str = json.dumps(data, sort_keys=True, indent=2)

    # Write with LF line endings (consistent with EPB canonicalization)
    output_path.write_text(json_str + "\n", encoding="utf-8", newline="")
