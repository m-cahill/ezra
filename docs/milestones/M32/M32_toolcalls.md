# M32 Tool Calls Log

Milestone: M32 — Reproducible Distribution Baseline

| Timestamp | Tool | Purpose | Files / Target | Status |
|-----------|------|---------|----------------|--------|
| 2026-03-03 | run | Create branch m32-reproducible-distribution | repo | Done |
| 2026-03-03 | run | pip-compile pyproject.toml --extra dev -o requirements.txt | requirements.txt | Done |
| 2026-03-03 | search_replace | CI: install from requirements.txt + pip install -e . | .github/workflows/ci.yml | Done |
| 2026-03-03 | search_replace | Pin actions to SHA (checkout, setup-python, upload/download-artifact, etc.) | .github/workflows/ci.yml | Done |
| 2026-03-03 | search_replace | Add parity/integration env-var sentence to §8 | docs/ezra.md | Done |
| 2026-03-03 | run | ruff, mypy, pytest (local); hermetic hash verified | repo | Done |
| 2026-03-03 | run | git commit (M32 impl), git push, gh pr create | repo / PR #33 | Done |
| 2026-03-03 | write | M32_run1.md (template, Run ID pending) | docs/milestones/M32/M32_run1.md | Done |
| 2026-03-03 | write | M32_audit.md | docs/milestones/M32/M32_audit.md | Done |
| 2026-03-03 | write | M32_summary.md | docs/milestones/M32/M32_summary.md | Done |
