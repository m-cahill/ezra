# Milestone Summary — M32

**Project:** EZRA  
**Phase:** XVIII — Distribution & Supply Chain Hardening  
**Milestone:** M32 — Reproducible Distribution Baseline  
**Timeframe:** 2026-03-03  
**Status:** Closed (pending CI Run 1 confirmation)  
**Baseline:** 027ef9c (main after M32 plan commit); M31 v1.0.0  
**Refactor Posture:** Behavior-Preserving

---

## 1. Milestone Objective

Close the remaining audit gaps identified in the M31 full codebase audit (4.75 → 5.0): introduce deterministic dependency locking, pin GitHub Actions to immutable SHAs, and document parity/integration test skip behavior. No runtime or EPB changes; packaging and governance only.

---

## 2. Scope Definition

### In Scope

- **Lockfile:** `pip-compile pyproject.toml --extra dev` → `requirements.txt` committed; all CI jobs that install the project use `pip install -r requirements.txt` + `pip install -e .`.
- **Actions:** Pin to full SHA: `actions/checkout`, `actions/setup-python`, `actions/upload-artifact`, `actions/download-artifact`, `actions/attest-build-provenance`, `actions/upload-pages-artifact`, `actions/deploy-pages`, `actions/dependency-review-action`, `gitleaks/gitleaks-action`, `ossf/scorecard-action`.
- **Docs:** One sentence in `docs/ezra.md` §8: parity and integration tests skipped unless `EZRA_RUN_PARITY=1` or `EZRA_RUN_INTEGRATION=1` is set.
- **Artifacts:** `requirements.txt`, updated `.github/workflows/ci.yml`, updated `docs/ezra.md`, `M32_run1.md`, `M32_audit.md`, `M32_summary.md`, `M32_toolcalls.md`.

### Out of Scope

- No CI threshold changes, no new CI jobs, no packaging split, no PyPI (M33), no RediAI integration, no performance work, no refactors, no code movement. Optional `docs/ci/CI_ARCHITECTURE.md` (≤15 LOC) not added.

---

## 3. Refactor Classification

**Change type:** Mechanical refactor (workflow and doc edits; lockfile add).  
**Observability:** None for runtime/EPB; only CI install path and action refs and one doc sentence.

---

## 4. Work Executed

- Generated `requirements.txt` via `pip-compile pyproject.toml --extra dev`.
- Updated every CI job that installs the project to use `pip install -r requirements.txt` and `pip install -e .` (lint, typecheck, epb-tools-minimal, test, security, sbom, complexity, determinism-check, docs-build).
- Replaced all tag-based action refs with full SHA in `.github/workflows/ci.yml`.
- Appended one sentence to `docs/ezra.md` §8.
- Branch `m32-reproducible-distribution`; PR #33 opened.
- No functional logic or application code changed.

---

## 5. Invariants & Compatibility

**Declared invariants (unchanged):** EPB schema, canonicalization logic, hashing logic, signing logic, plugin interfaces, zone registry format, CI enforcement thresholds, coverage threshold (85%), determinism checks, hermetic reproducibility logic.

**Compatibility:** Backward compatible. No breaking changes. No deprecations.

---

## 6. Validation & Evidence

| Evidence Type   | Tool/Workflow        | Result   | Notes                                      |
|-----------------|----------------------|----------|--------------------------------------------|
| Lint            | ruff check/format    | Pass     | Local                                      |
| Type check      | mypy src             | Pass     | Local                                      |
| Tests           | pytest               | 253 pass, 28 skip | Local; coverage 85.54%             |
| Hermetic hash   | Inline script (same as CI) | Unchanged | `c186777c33b7b7b9d11540bda7398efd0dfb085143506513a4ce87836c6ac7c2` |
| CI Run 1        | GitHub Actions       | Pending  | PR #33                                     |

---

## 7. CI / Automation Impact

- **Workflows affected:** CI only; install steps and action refs.
- **Checks:** None added/removed/reclassified; no enforcement change.
- **Signal:** Deterministic installs; actions immutable by SHA.

---

## 8. Issues, Exceptions, and Guardrails

No new issues introduced. Guardrails: lockfile and SHA pinning enforce reproducibility and supply-chain immutability.

---

## 9. Deferred Work

None.

---

## 10. Governance Outcomes

- Reproducible dependency graph (one lockfile, one truth).
- Workflow actions pinned to SHA (audit score CI-001 closed).
- Parity/integration skip behavior documented (DOC-001 closed).
- Audit score path to 5.0 (DEPS-001, CI-001, DOC-001 closed).

---

## 11. Exit Criteria Evaluation

| Criterion | Status   | Evidence |
|-----------|----------|----------|
| Lockfile committed and used in CI | Met | `requirements.txt` in repo; all install steps updated |
| Actions pinned to SHA | Met | All critical actions use full SHA |
| Docs updated | Met | §8 sentence added |
| CI passes, no threshold weakening | Pending | Run 1 for PR #33 |
| Deterministic bundle hash unchanged | Met | No hashing/canonicalization change; local hash unchanged |
| No change to EPB artifacts | Met | No EPB/schema/code change |

---

## 12. Final Verdict

Milestone objectives met. Refactor is packaging and governance only; invariants preserved. Hermetic hash and determinism unchanged; coverage gate met locally. **Proceed to merge after CI Run 1 is green.**

---

## 13. Authorized Next Step

- Merge PR #33 after CI green and express permission (per .cursorrules).
- Then M33 — PyPI + Provenance (Trusted Publishing, release on tag, SBOM, version/tag consistency).

---

## 14. Canonical References

- **Branch:** m32-reproducible-distribution  
- **Commit:** 6bcc84f (M32: Reproducible distribution baseline — lockfile, action SHA pinning, doc env-var)  
- **PR:** #33 — M32: Reproducible Distribution Baseline  
- **CI Run:** *To be filled after Run 1*  
- **Plan:** docs/milestones/M32/M32_plan.md  
- **Audit:** docs/milestones/M32/M32_audit.md  
