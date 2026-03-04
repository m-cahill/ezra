# M33 Tool Calls Log

Milestone: M33 — Reproducible Distribution Artifacts & Trusted Publishing

| Timestamp | Tool | Purpose | Files / Target | Status |
|-----------|------|---------|----------------|--------|
| 2026-03-03 | run | Create branch m33-reproducible-artifacts | repo | Done |
| 2026-03-03 | write | Add release workflow with SHA pins | .github/workflows/release.yml | Done |
| 2026-03-03 | write | PyPI Trusted Publishing setup instructions | docs/release/PYPI_TRUSTED_PUBLISHING.md | Done |
| 2026-03-03 | run | git commit, push, gh pr create | repo / PR #34 | Done |
| 2026-03-04 | run | gh pr view / gh run view (CI status) | PR #34, Run 22654936020 | Done |
| 2026-03-04 | write | M33_run1.md — CI workflow analysis | docs/milestones/M33/M33_run1.md | Done |
| 2026-03-04 | search_replace | Quick wins: contract tests → ezra.epb_tools (verify, certify, generate_cert_metadata) | tests/contracts/*.py | Done |
| 2026-03-04 | search_replace | Suppress DeprecationWarning for legacy modules in public surface freeze test | tests/test_public_surface_freeze.py | Done |
| 2026-03-04 | write | CI architecture doc | docs/CI_ARCHITECTURE.md | Done |
| 2026-03-04 | search_replace | Release process link in §8 | docs/ezra.md | Done |
| 2026-03-04 | search_replace | Releases section | README.md | Done |
| 2026-03-04 | run | ruff, mypy, pytest, coverage | repo | Done |
| 2026-03-04 | run | gh pr view / gh run list (CI Run 2) | PR #34, Run 22655694366 | Done |
| 2026-03-04 | write | M33_run2.md — CI workflow analysis (polish commit) | docs/milestones/M33/M33_run2.md | Done |
