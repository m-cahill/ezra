# Milestone Summary — M37A

**Project:** EZRA  
**Milestone:** M37A — Required Gate Recovery for Public Release  
**Refactor Posture:** Planning-only (no implementation)  
**Status:** Closed — planning complete; implementation deferred to **M37B**  

---

## Objective

Plan behavior-preserving recovery for **post-M36** red default-branch CI gates (`pip-audit`, Distribution Verification HTTP 401, Dependency Review availability, SLSA provenance / attestation limits, supplemental Pages), without changing runtime, workflows, or dependencies.

---

## Summary (required statements)

1. **M37A was planning-only.** No fixes were implemented in this milestone.
2. **No runtime, schema, workflow, dependency, `.gitignore`, or secret-boundary cleanup changes were made.**
3. **M37A identified the gate recovery implementation scope:** documented in `M37A_plan.md` (recovery matrix + four primary tracks + supplemental Pages).
4. **M37 remains deferred until gate recovery is resolved or explicitly accepted as red** for public-release trust in `main`.
5. **The next recommended milestone is M37B** — Required Gate Recovery Implementation.

---

## Deliverables

| Artifact | Purpose |
| --- | --- |
| `docs/milestones/M37A/M37A_plan.md` | Intent, scope, investigation, recovery tracks, risk, exit criteria, recovery matrix |
| `docs/milestones/M37A/M37A_run1.md` | Command evidence: `git`, `gh`, `pip-audit`, CI run `25466391573`, branch protection API |
| `docs/milestones/M37A/M37A_toolcalls.md` | Tool call log per `.cursorrules` |
| `docs/milestones/M37A/M37A_summary.md` | This document |
| `docs/milestones/M37A/M37A_audit.md` | Milestone audit / acceptance |
| `REFACTOR.md` | M37A / M37B ledger updates |
| `docs/ezra.md` | Milestone index rows |

---

## Gate evidence (from M37A_run1 / PR #38 CI)

| Gate | Class |
| --- | --- |
| Security / `pip-audit` | **Real** supply-chain: 11 vulnerabilities in 6 packages |
| Distribution Verification | **HTTP 401** on Actions artifact ZIP download |
| Dependency Review | **PR-only**; fails when GHAS / dependency graph unavailable |
| SLSA Provenance | **Skipped** on PR; on `main`, GitHub blocks attestation for **user-owned private** repos |
| Documentation Deploy | **Settings** (Pages not enabled) on representative runs |

PR #38 CI (`mergeStateStatus: UNSTABLE`) matches the same failure classes; no new failure mode attributable to M37A docs.

---

## Closeout: ensure all documentation is updated as necessary

Ledger updates in **this closeout commit** complete the planning record: `REFACTOR.md`, `docs/ezra.md`, `M37A_summary.md`, `M37A_audit.md`, and **M37B** plan stubs (`M37B_plan.md`, `M37B_toolcalls.md`). Prior milestone artifacts (`M37A_plan.md`, `M37A_run1.md`) remain the technical source of truth for evidence.

---

## Prompt templates note

The closeout handoff referenced:

- `docs/prompts/summaryprompt.md`
- `docs/prompts/unifiedmilestoneauditpromptV2.md`

Those paths **do not exist** in the repository (the `docs/prompts/` tree is listed in `.gitignore`). This summary follows the **explicit M37A closeout requirements** from the maintainer handoff and the same structural pattern as `docs/milestones/M36/M36_summary.md`.

---

## Authorized next milestone

**M37B — Required Gate Recovery Implementation** — authorized as the next **implementation** milestone (see `M37B_plan.md`). **M37** secret-boundary cleanup stays deferred until gate recovery is implemented or explicitly accepted.

---

## Closeout commit verification (2026-05-06, local)

| Command | Result |
| --- | --- |
| `ruff format --check .` | Pass |
| `pytest -q` | Pass (267 passed, 28 skipped) |
| `ruff check .` | **Fail** — pre-existing `UP038` in `tests/test_baseline_schema.py` (not introduced by M37A closeout docs) |

