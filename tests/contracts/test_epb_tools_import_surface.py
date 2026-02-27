"""EPB tools import surface isolation tests.

Asserts that importing ezra.epb_tools does NOT pull in runtime, plugins, or ML
dependencies. Required for M28 artifact-only distribution mode.
"""

from __future__ import annotations

import sys


def test_epb_tools_import_surface_no_runtime_or_ml() -> None:
    """Importing ezra.epb_tools must not load core, plugins, torch, or easyocr."""
    preexisting = set(sys.modules)

    # Clear only EPB-tool-related modules so other test module state remains intact.
    for mod in list(sys.modules.keys()):
        if mod.startswith("ezra.epb_tools") or mod in (
            "ezra.tools.epb_certify",
            "ezra.tools.epb_verify",
            "ezra.tools.epb_generate_cert_metadata",
            "ezra.tools._epb_hash",
            "torch",
            "easyocr",
        ):
            del sys.modules[mod]

    import ezra.epb_tools.epb_certify  # noqa: F401
    import ezra.epb_tools.epb_generate_cert_metadata  # noqa: F401
    import ezra.epb_tools.epb_verify  # noqa: F401

    assert not ("ezra.core" in sys.modules and "ezra.core" not in preexisting), (
        "ezra.epb_tools must not import ezra.core"
    )
    assert not ("ezra.plugins" in sys.modules and "ezra.plugins" not in preexisting), (
        "ezra.epb_tools must not import ezra.plugins"
    )
    assert not ("torch" in sys.modules and "torch" not in preexisting), (
        "ezra.epb_tools must not import torch"
    )
    assert not ("easyocr" in sys.modules and "easyocr" not in preexisting), (
        "ezra.epb_tools must not import easyocr"
    )
