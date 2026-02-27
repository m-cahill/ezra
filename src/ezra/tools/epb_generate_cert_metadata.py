"""Legacy wrapper: EPB certification metadata moved to ezra.epb_tools.epb_generate_cert_metadata.

This module is deprecated. Use ezra.epb_tools.epb_generate_cert_metadata instead.
"""

from __future__ import annotations

import sys
import warnings

from ezra.epb_tools.epb_generate_cert_metadata import (
    generate_cert_metadata,
    main,
    write_canonical_cert_json,
)

warnings.warn(
    "epb tools moved to ezra.epb_tools; ezra.tools.epb_generate_cert_metadata is deprecated",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["generate_cert_metadata", "write_canonical_cert_json", "main"]

if __name__ == "__main__":
    sys.exit(main())
