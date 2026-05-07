"""Public release boundary guardrails."""

from __future__ import annotations

import subprocess


def test_company_secret_paths_not_tracked() -> None:
    """Approved company-secret paths must not be tracked in the public repo."""
    result = subprocess.run(
        ["git", "ls-files", ".cursorrules", "docs/enhancements", "docs/prompts"],
        check=True,
        capture_output=True,
        text=True,
    )
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    assert tracked == [], (
        "Company-secret paths must not be tracked in the public repo: " + ", ".join(tracked)
    )
