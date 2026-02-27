"""EPB tools import surface isolation tests.

Asserts that importing ezra.epb_tools does NOT pull in runtime, plugins, or ML
dependencies. Required for M28 artifact-only distribution mode.
"""

from __future__ import annotations

import sys


def test_epb_tools_import_surface_no_runtime_or_ml() -> None:
    """Importing ezra.epb_tools must not load core, plugins, torch, or easyocr."""
    # Clear any prior imports so we observe only what epb_tools pulls in
    for mod in list(sys.modules.keys()):
        if mod.startswith("ezra.") or mod in ("torch", "easyocr"):
            del sys.modules[mod]

    import ezra.epb_tools.epb_certify  # noqa: F401
    import ezra.epb_tools.epb_generate_cert_metadata  # noqa: F401
    import ezra.epb_tools.epb_verify  # noqa: F401

    assert "ezra.core" not in sys.modules, "ezra.epb_tools must not import ezra.core"
    assert "ezra.plugins" not in sys.modules, "ezra.epb_tools must not import ezra.plugins"
    assert "torch" not in sys.modules, "ezra.epb_tools must not import torch"
    assert "easyocr" not in sys.modules, "ezra.epb_tools must not import easyocr"
