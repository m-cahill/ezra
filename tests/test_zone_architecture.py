"""Architecture boundary tests for zone module.

Ensures that runtime (core) does not import zone registry internals directly.
"""

import ast
from pathlib import Path


def test_core_does_not_import_registry_internals():
    """Test that core module does not import zone registry internals.

    Core should only import from ezra.zones (public __init__.py).
    """
    core_dir = Path(__file__).parent.parent / "src" / "ezra" / "core"

    forbidden_imports = [
        "ezra.zones.registry",
        "ezra.zones.validator",
    ]

    # Check all Python files in core directory
    for py_file in core_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue

        content = py_file.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(py_file))

        # Find all import statements
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in forbidden_imports:
                        raise AssertionError(
                            f"{py_file} imports {alias.name} directly. "
                            "Core should only import from ezra.zones (public API)."
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.module in forbidden_imports:
                    raise AssertionError(
                        f"{py_file} imports from {node.module} directly. "
                        "Core should only import from ezra.zones (public API)."
                    )


def test_zones_projector_does_not_import_epb():
    """Test that zones.projector does not import epb internals.

    Projector should remain independent of EPB module to preserve
    zone schema portability.
    """
    projector_file = Path(__file__).parent.parent / "src" / "ezra" / "zones" / "projector.py"

    forbidden_imports = [
        "ezra.epb",
        "ezra.epb.builder",
        "ezra.epb.canonical",
        "ezra.epb.hasher",
        "ezra.epb.hash_verifier",
        "ezra.epb.schema_validator",
        "ezra.epb.writer",
        "ezra.epb.zone_adapter",
    ]

    content = projector_file.read_text(encoding="utf-8")
    tree = ast.parse(content, filename=str(projector_file))

    # Find all import statements
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in forbidden_imports:
                    raise AssertionError(
                        f"{projector_file} imports {alias.name} directly. "
                        "Projector should not depend on EPB internals."
                    )
        elif isinstance(node, ast.ImportFrom):
            if node.module in forbidden_imports:
                raise AssertionError(
                    f"{projector_file} imports from {node.module} directly. "
                    "Projector should not depend on EPB internals."
                )


def test_zones_public_api_available():
    """Test that zones public API is accessible from core."""
    # This test ensures the public API exists and is importable
    from ezra.zones import (
        BBoxNorm,
        ZonePersistence,
        ZoneRegistry,
        ZoneSchema,
        export_zone_schema_json,
        project_state_to_zones,
        to_projection_canonical_json,
    )

    # Verify types exist
    assert BBoxNorm is not None
    assert ZonePersistence is not None
    assert ZoneSchema is not None
    assert ZoneRegistry is not None
    assert export_zone_schema_json is not None
    assert project_state_to_zones is not None
    assert to_projection_canonical_json is not None
