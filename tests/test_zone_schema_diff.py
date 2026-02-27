"""Schema diff enforcement tests.

This module tests that schema_v1.json matches the committed snapshot baseline.
Any schema change must be explicitly acknowledged by updating the snapshot
in the same milestone that changes the schema.

This is a golden file workflow: the snapshot is the source of truth, and
any drift from the snapshot fails the test.
"""

from __future__ import annotations

import importlib.resources
import json
from pathlib import Path

import pytest


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
        Path(__file__).parent.parent / "docs" / "baselines" / "zone_schema_snapshot.json"
    )
    snapshot_text = snapshot_path.read_text(encoding="utf-8")
    snapshot = json.loads(snapshot_text)
    return snapshot


def test_schema_matches_snapshot():
    """Test that schema_v1.json matches the committed snapshot.

    This test enforces that any schema change requires an explicit snapshot
    update. The snapshot is the source of truth, and drift fails the test.

    If this test fails, it means:
    1. schema_v1.json was modified, OR
    2. The snapshot was not updated to match the new schema

    Resolution:
    - If schema change is intentional: update zone_schema_snapshot.json
      to match the new schema (canonical re-serialization) in the same
      milestone that changes the schema.
    - If schema change is unintentional: revert schema_v1.json changes.
    """
    current_schema = _load_schema_canonical()
    snapshot_schema = _load_snapshot_canonical()

    # Canonical comparison: serialize both with sorted keys
    current_canonical = json.dumps(current_schema, sort_keys=True, indent=2)
    snapshot_canonical = json.dumps(snapshot_schema, sort_keys=True, indent=2)

    if current_canonical != snapshot_canonical:
        # Provide helpful error message
        msg = (
            "schema_v1.json does not match zone_schema_snapshot.json.\n"
            "This indicates a schema change without snapshot update.\n\n"
            "If this change is intentional:\n"
            "1. Update docs/baselines/zone_schema_snapshot.json to match the new schema\n"
            "2. Ensure SCHEMA_VERSION is bumped in the same milestone\n"
            "3. Document the change in the milestone plan\n\n"
            "If this change is unintentional:\n"
            "1. Revert changes to schema_v1.json\n"
        )
        pytest.fail(msg)

    # If we get here, schemas match
    assert current_canonical == snapshot_canonical
