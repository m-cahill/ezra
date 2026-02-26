"""Architecture boundary tests for zone module.

Ensures that runtime (core) does not import zone registry internals directly.
"""

import ast
import importlib.util
from pathlib import Path


def test_core_does_not_import_registry_internals():
    """Test that core module does not import zone registry internals.

    Core should only import from ezra.zones (public __init__.py).
    """
    core_dir = Path(__file__).parent.parent / "src" / "ezra" / "core"
    zones_registry_path = Path(__file__).parent.parent / "src" / "ezra" / "zones" / "registry.py"
    zones_validator_path = Path(__file__).parent.parent / "src" / "ezra" / "zones" / "validator.py"

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


def test_zones_public_api_available():
    """Test that zones public API is accessible from core."""
    # This test ensures the public API exists and is importable
    from ezra.zones import (
        BBoxNorm,
        ZonePersistence,
        ZoneRegistry,
        ZoneSchema,
        export_zone_schema_json,
    )

    # Verify types exist
    assert BBoxNorm is not None
    assert ZonePersistence is not None
    assert ZoneSchema is not None
    assert ZoneRegistry is not None
    assert export_zone_schema_json is not None

