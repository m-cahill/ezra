"""Legacy wrapper: EPB verification moved to ezra.epb_tools.epb_verify.

This module is deprecated. Use ezra.epb_tools.epb_verify instead.
"""

from __future__ import annotations

import sys
import warnings

from ezra.epb_tools.epb_verify import DEFAULT_SIG_FILENAME, main, verify_bundle

warnings.warn(
    "epb tools moved to ezra.epb_tools; ezra.tools.epb_verify is deprecated",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["DEFAULT_SIG_FILENAME", "verify_bundle", "main"]

if __name__ == "__main__":
    sys.exit(main())
