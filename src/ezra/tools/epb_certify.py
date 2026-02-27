"""Legacy wrapper: EPB certification moved to ezra.epb_tools.epb_certify.

This module is deprecated. Use ezra.epb_tools.epb_certify instead.
"""

from __future__ import annotations

import sys
import warnings

from ezra.epb_tools.epb_certify import certify, main

warnings.warn(
    "epb tools moved to ezra.epb_tools; ezra.tools.epb_certify is deprecated",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["certify", "main"]

if __name__ == "__main__":
    sys.exit(main())
