"""Tests for EZRA package version in EPB manifest (M38)."""

from __future__ import annotations

import importlib.metadata
import re
from unittest.mock import patch

from ezra import __version__ as ezra_dunder_version
from ezra.epb.builder import EPB_VERSION, build_epb_bundle

_MANIFEST_EZRA_VERSION_PATTERN = re.compile(r"^v\d+\.\d+\.\d+(-\w+)?$")


def test_manifest_epb_version_unchanged() -> None:
    """EPB artifact version in manifest must remain locked."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )
    assert bundle["manifest"]["epb_version"] == EPB_VERSION
    assert EPB_VERSION == "1.0.0"


def test_manifest_ezra_version_matches_package_metadata() -> None:
    """When installed, manifest ezra_version must track distribution metadata."""
    pkg = importlib.metadata.version("ezra")
    expected = pkg if pkg.startswith("v") else f"v{pkg}"
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )
    assert bundle["manifest"]["ezra_version"] == expected
    assert _MANIFEST_EZRA_VERSION_PATTERN.match(bundle["manifest"]["ezra_version"])


def test_manifest_ezra_version_fallback_when_metadata_missing() -> None:
    """If distribution metadata is missing, fall back to ezra.__version__."""
    with patch(
        "ezra.epb.builder.importlib.metadata.version",
        side_effect=importlib.metadata.PackageNotFoundError,
    ):
        bundle = build_epb_bundle(
            detections=[],
            plugin_name="test",
            plugin_version="1.0.0",
            input_metadata={"width": 100, "height": 200, "channels": 3},
        )
    expected = (
        ezra_dunder_version if ezra_dunder_version.startswith("v") else f"v{ezra_dunder_version}"
    )
    assert bundle["manifest"]["ezra_version"] == expected
