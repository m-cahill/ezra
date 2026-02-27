"""EPB bundle builder for assembling in-memory bundle dictionaries.

This module builds EPB v1.0.0 bundle structures from plugin detections
and structured state. No disk I/O is performed here.
"""

from __future__ import annotations

import platform
import sys
from datetime import UTC, datetime
from types import MappingProxyType
from typing import Any

# EPB v1.0.0 version string (immutable per spec)
EPB_VERSION = "1.0.0"


def build_epb_bundle(
    detections: list[dict[str, Any]],
    plugin_name: str,
    plugin_version: str,
    input_metadata: dict[str, Any],
    state: dict[str, Any] | None = None,
    delta: dict[str, Any] | None = None,
    timestamp: datetime | None = None,
) -> MappingProxyType[str, Any]:
    """Build an in-memory EPB v1.0.0 bundle dictionary.

    Args:
        detections: List of detection dictionaries from plugin.infer().
        plugin_name: Name of the plugin used (e.g., "easyocr", "tesseract").
        plugin_version: Version string of the plugin.
        input_metadata: Input image metadata (width, height, channels, etc.).
        state: Optional structured state dictionary (domain-agnostic).
        delta: Optional delta dictionary (incremental state changes).
        timestamp: Optional explicit timestamp (defaults to current UTC time).

    Returns:
        Dictionary containing EPB bundle structure:
        {
            "manifest": {...},
            "detections": {...},
            "state": {...} or None,
            "delta": {...} or None,
        }
    """
    ts = timestamp or datetime.now(UTC)
    timestamp_str = ts.isoformat().replace("+00:00", "Z")

    # Build manifest.json structure
    manifest: dict[str, Any] = {
        "epb_version": EPB_VERSION,
        "ezra_version": "v0.0.8-m07",  # TODO: Get from package metadata
        "timestamp": timestamp_str,
        "plugin_versions": {
            plugin_name: {
                "name": plugin_name,
                "version": plugin_version,
            }
        },
        "input_metadata": input_metadata,
        "platform": platform.platform(),
        "python_version": sys.version.split()[0],
    }

    # Build detections.json structure
    detections_dict: dict[str, Any] = {
        "detections": detections,
    }

    # Build state.json structure (always present, minimal if not provided)
    if state is None:
        state = {}
    state_dict: dict[str, Any] = {
        "version": "1.0.0",  # State schema version
        "timestamp": timestamp_str,
        **state,  # Merge in provided state fields
    }

    # Build delta.json structure (if provided)
    delta_dict: dict[str, Any] | None = delta

    # Seal all nested dicts with MappingProxyType for immutability
    # (top-level only, not recursive)
    sealed_manifest = MappingProxyType(manifest)
    sealed_detections = MappingProxyType(detections_dict)
    sealed_state = MappingProxyType(state_dict)
    sealed_delta = MappingProxyType(delta_dict) if delta_dict is not None else None

    # Build bundle dict and seal it
    bundle: dict[str, Any] = {
        "manifest": sealed_manifest,
        "detections": sealed_detections,
        "state": sealed_state,  # Always present (minimal if None provided)
        "delta": sealed_delta,  # Optional (None if not provided)
    }

    # Return sealed bundle (top-level dict sealed, nested dicts also sealed)
    return MappingProxyType(bundle)
