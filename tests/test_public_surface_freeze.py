"""Public surface freeze tests for EZRA.

Tests that EZRA's public runtime surfaces (module exports, exception hierarchy,
EPB version, EPB schemas) remain frozen and prevent accidental drift.
"""

import hashlib
import importlib
import inspect
import json
import pkgutil
import warnings
from pathlib import Path
from typing import Any

import ezra
from ezra.epb.builder import EPB_VERSION

# Legacy EPB tool wrappers (ezra.tools.epb_*) emit DeprecationWarning; suppress
# when we import-all for surface snapshot so test run stays warning-clean.
_DEPRECATED_EPB_TOOL_MODULES = frozenset(
    {
        "ezra.tools.epb_certify",
        "ezra.tools.epb_generate_cert_metadata",
        "ezra.tools.epb_verify",
    }
)


def _discover_all_modules() -> list[str]:
    """Discover all importable modules under ezra package.

    Returns:
        Sorted list of module names (e.g., ['ezra.core.engine', 'ezra.epb.builder', ...]).
    """
    modules = []
    for importer, modname, ispkg in pkgutil.walk_packages(ezra.__path__, prefix="ezra."):
        if not ispkg:
            modules.append(modname)
    return sorted(modules)


def _import_all_modules(module_names: list[str]) -> None:
    """Import all modules to ensure exception subclasses are registered."""
    for modname in module_names:
        try:
            with warnings.catch_warnings():
                if modname in _DEPRECATED_EPB_TOOL_MODULES:
                    warnings.simplefilter("ignore", DeprecationWarning)
                importlib.import_module(modname)
        except (ImportError, AttributeError):
            # Skip modules that can't be imported (e.g., optional dependencies)
            pass


def _build_exception_hierarchy() -> dict[str, Any]:
    """Build exception hierarchy tree from EzraError.

    Returns:
        Dictionary mapping exception class names to their direct base classes.
    """
    from ezra.errors import EzraError

    # Import all modules first to ensure subclasses are registered
    module_names = _discover_all_modules()
    _import_all_modules(module_names)

    def _get_subclasses(cls: type) -> list[type]:
        """Recursively get all subclasses."""
        subclasses = []
        for subclass in cls.__subclasses__():
            subclasses.append(subclass)
            subclasses.extend(_get_subclasses(subclass))
        return subclasses

    hierarchy: dict[str, Any] = {}
    all_exceptions = [EzraError] + _get_subclasses(EzraError)

    for exc_class in sorted(all_exceptions, key=lambda x: x.__name__):
        # Get direct bases (excluding object)
        bases = [
            base.__name__
            for base in exc_class.__bases__
            if base is not object and base.__name__ != "Exception"
        ]
        hierarchy[exc_class.__name__] = {
            "bases": sorted(bases),
            "module": exc_class.__module__,
        }

    return hierarchy


def _get_ezra_error_public_attributes() -> list[str]:
    """Get public attributes defined in errors.py module.

    Returns:
        Sorted list of public attribute names (excluding private/dunder).
    """
    import ezra.errors

    public_attrs = []
    for name in dir(ezra.errors):
        if not name.startswith("_") and not name.startswith("__"):
            # Get the actual object to check if it's defined in this module
            obj = getattr(ezra.errors, name)
            if inspect.isclass(obj) and obj.__module__ == "ezra.errors":
                public_attrs.append(name)

    return sorted(public_attrs)


def _compute_schema_checksums() -> dict[str, str]:
    """Compute SHA256 checksums for all EPB schema files.

    Returns:
        Dictionary mapping schema filenames to their SHA256 hashes.
    """
    schema_dir = Path(__file__).parent.parent / "docs" / "specs" / "epb_v1" / "schemas"
    checksums: dict[str, str] = {}

    if schema_dir.exists():
        for schema_file in sorted(schema_dir.glob("*.schema.json")):
            content = schema_file.read_bytes()
            sha256 = hashlib.sha256(content).hexdigest()
            checksums[schema_file.name] = sha256

    return checksums


def _capture_public_surface() -> dict[str, Any]:
    """Capture current public surface snapshot.

    Returns:
        Dictionary containing:
        - modules: sorted list of all module names
        - exception_hierarchy: exception class tree
        - exception_public_attrs: public attributes from errors.py
        - epb_version: EPB version string
        - epb_schemas: schema file checksums
    """
    modules = _discover_all_modules()
    exception_hierarchy = _build_exception_hierarchy()
    exception_public_attrs = _get_ezra_error_public_attributes()
    epb_schemas = _compute_schema_checksums()

    return {
        "modules": modules,
        "exception_hierarchy": exception_hierarchy,
        "exception_public_attrs": exception_public_attrs,
        "epb_version": EPB_VERSION,
        "epb_schemas": epb_schemas,
    }


def test_public_surface_freeze():
    """Test that public surface matches committed snapshot.

    This test enforces Release Lock posture by preventing accidental drift in:
    - Module structure (no new modules without milestone)
    - Exception hierarchy (no new exceptions without milestone)
    - EPB version (must remain 1.0.0)
    - EPB schemas (no schema changes without milestone)
    """
    snapshot_path = (
        Path(__file__).parent.parent / "docs" / "baselines" / "public_surface_snapshot.json"
    )

    # Capture current surface
    current_surface = _capture_public_surface()

    # Load or create snapshot
    if snapshot_path.exists():
        snapshot_data = json.loads(snapshot_path.read_text(encoding="utf-8"))
        # Compare
        if current_surface != snapshot_data:
            # Generate clear diff message
            current_json = json.dumps(current_surface, sort_keys=True, indent=2)
            snapshot_json = json.dumps(snapshot_data, sort_keys=True, indent=2)

            error_msg = (
                "Public surface changed. Update snapshot only within an explicit milestone.\n\n"
                f"Expected snapshot at: {snapshot_path}\n\n"
                "To update snapshot (only within a milestone):\n"
                "1. Review the changes carefully\n"
                "2. Ensure milestone explicitly justifies the change\n"
                "3. Manually update docs/baselines/public_surface_snapshot.json\n"
                "4. Re-run tests to verify\n\n"
                "Current surface:\n"
                f"{current_json}\n\n"
                "Expected surface:\n"
                f"{snapshot_json}"
            )
            raise AssertionError(error_msg)
    else:
        # First run: write snapshot
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        json_str = json.dumps(current_surface, sort_keys=True, indent=2)
        snapshot_path.write_text(json_str + "\n", encoding="utf-8", newline="")
        # Re-read to verify
        snapshot_data = json.loads(snapshot_path.read_text(encoding="utf-8"))
        assert current_surface == snapshot_data, "Failed to write snapshot correctly"
