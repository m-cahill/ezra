# M36 Tool Calls

| Timestamp (UTC) | Tool | Purpose | Files/Target | Status |
| --- | --- | --- | --- | --- |
| 2026-03-20 | — | Scaffold created at M35 closeout; no M36 work started | — | — |
| 2026-05-06 | Read / Glob | Gather plan, audits, `.cursorrules`, milestone stubs | `docs/M33fullaudit.md`, `docs/milestones/M36/*` | Done |
| 2026-05-06 | Shell | M36 verification: `git status`, `rev-parse`, `ls-files`, `diff` | repo root | Done |
| 2026-05-06 | Shell | Local quality: `ruff`, `mypy`, `pytest` | repo root | Done (`mypy` failed locally; see `M36_run1.md`) |
| 2026-05-06 | Write / StrReplace | M36 artifacts: reconciliation, REFACTOR ledger, run/summary/audit, M37 stubs, `ezra.md` row | `docs/release/`, `docs/milestones/M36/`, `docs/milestones/M37/`, `REFACTOR.md`, `docs/ezra.md` | Done |
| 2026-05-06 | Shell | Stage M36 deliverables (`git add`, `git add -f` for new ignored `docs/milestones/*` paths) | repo root | Done |
| 2026-05-07 | StrReplace | Clarify `git status` timing in `M36_run1.md` (pre-artifact snapshot vs final §4 file list) | `docs/milestones/M36/M36_run1.md` | Done |
