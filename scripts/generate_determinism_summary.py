#!/usr/bin/env python3
"""Generate determinism gate summary for GitHub Actions step summary.

This script reads determinism_report.json and outputs formatted summary
to GitHub Actions step summary format.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    """Main entry point."""
    report_path = Path("determinism_output/determinism_report.json")

    if not report_path.exists():
        print("Warning: determinism_report.json not found", file=sys.stderr)
        return 0

    with report_path.open(encoding="utf-8") as f:
        report = json.load(f)

    check = report["determinism_check"]
    print(f"Result: {check['result']}")
    print(f"Number of runs: {check['num_runs']}")
    print()

    for i in range(check["num_runs"]):
        run_key = f"run_{i + 1}"
        run_info = check["hashes"][run_key]
        print(f"SHA{i + 1} ({run_info['bundle_dir']}): {run_info['sha256']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
