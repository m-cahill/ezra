"""Schema version coupling enforcement tests.

This module enforces that schema changes and version bumps are coupled:
- If schema changes, version must change
- If version changes, schema must change

This prevents:
- Silent schema drift without version bump
- Version bumps without actual schema changes
"""

from __future__ import annotations

import importlib.resources
import json
from pathlib import Path

import pytest

from ezra.zones.serialize import SCHEMA_VERSION


def _load_schema_canonical() -> dict:
    """Load schema_v1.json and return canonical dict."""
    schema_text = (
        importlib.resources.files("ezra.zones")
        .joinpath("schema_v1.json")
        .read_text(encoding="utf-8")
    )
    schema = json.loads(schema_text)
    return schema


def _load_snapshot_canonical() -> dict:
    """Load zone_schema_snapshot.json and return canonical dict."""
    snapshot_path = (
        Path(__file__).parent.parent
        / "docs"
        / "baselines"
        / "zone_schema_snapshot.json"
    )
    snapshot_text = snapshot_path.read_text(encoding="utf-8")
    snapshot = json.loads(snapshot_text)
    return snapshot


def _get_schema_version_from_schema(schema: dict) -> str | None:
    """Extract version from schema title or metadata if present.

    Returns:
        Version string if found in schema, None otherwise.
    """
    # Check title for version pattern
    title = schema.get("title", "")
    if "v" in title.lower():
        # Try to extract version from title like "EZRA Universal Zone Mapping Schema v1.0.0"
        parts = title.split()
        for part in parts:
            if part.startswith("v") and part[1:].replace(".", "").isdigit():
                return part[1:]  # Return version without "v" prefix
    return None


def test_version_schema_coupling():
    """Test that schema changes require version bumps and vice versa.

    This test enforces bidirectional coupling:
    1. If schema changed (vs snapshot) AND version unchanged → FAIL
    2. If version changed AND schema unchanged (vs snapshot) → FAIL

    Both conditions must be true for a valid schema evolution:
    - Schema changed → version must change
    - Version changed → schema must change
    """
    current_schema = _load_schema_canonical()
    snapshot_schema = _load_snapshot_canonical()

    # Canonical comparison
    current_canonical = json.dumps(current_schema, sort_keys=True, indent=2)
    snapshot_canonical = json.dumps(snapshot_schema, sort_keys=True, indent=2)

    schema_changed = current_canonical != snapshot_canonical

    # Get version from schema title (if present) for comparison
    # Note: SCHEMA_VERSION constant is the source of truth, but we check
    # schema title for consistency
    schema_version_in_title = _get_schema_version_from_schema(current_schema)
    snapshot_version_in_title = _get_schema_version_from_schema(snapshot_schema)

    # Check coupling rules
    violations = []

    # Baseline version (hardcoded - this is the initial version from M21)
    baseline_version = "1.0.0"

    # Rule 1: Schema changed but version unchanged
    # If schema changed from snapshot, version must have changed from baseline
    if schema_changed and SCHEMA_VERSION == baseline_version:
        violations.append(
            "Schema changed but SCHEMA_VERSION is still '1.0.0'. "
            "Version must be bumped when schema changes."
        )

    # Rule 2: Version changed but schema unchanged
    # This is harder to detect without git history, but we can check if
    # version in schema title changed while schema content didn't
    # Note: This is a best-effort check; the primary enforcement is Rule 1
    if not schema_changed:
        if schema_version_in_title and snapshot_version_in_title:
            if schema_version_in_title != snapshot_version_in_title:
                violations.append(
                    "Version in schema title changed but schema content unchanged. "
                    "Version bumps must accompany schema changes."
                )
        # Also check if SCHEMA_VERSION constant changed but schema didn't
        if SCHEMA_VERSION != baseline_version:
            violations.append(
                f"SCHEMA_VERSION changed to '{SCHEMA_VERSION}' but schema content unchanged. "
                "Version bumps must accompany schema changes."
            )

    if violations:
        msg = (
            "Version-schema coupling violation detected:\n\n"
            + "\n".join(f"- {v}" for v in violations)
            + "\n\n"
            "Resolution:\n"
            "1. If schema changed: bump SCHEMA_VERSION and update snapshot\n"
            "2. If version changed: ensure schema actually changed and update snapshot\n"
            "3. Both changes must occur in the same milestone\n"
        )
        pytest.fail(msg)

    # If we get here, coupling is correct
    # (Either both changed together, or neither changed)
    assert not violations

