📌 Milestone Summary — M25: EPB Consumer Certification & Artifact Reproducibility Hardening
=============================================================================================

**Project:** EZRA (Extensible Zone-Based Runtime Architecture)  
**Phase:** Phase V — Release Lock  
**Milestone:** M25 — EPB Consumer Certification & Artifact Reproducibility Hardening  
**Timeframe:** 2026-02-26 → 2026-02-27  
**Status:** Closed  
**Baseline:** `v0.0.25-m24` (tag)  
**Refactor Posture:** Behavior-Preserving (stdlib-only certification utility and contract tests; no runtime or schema changes)

---

## 1. Milestone Objective

**Why this milestone existed:**

After M24, EZRA had an explicit consumer contract harness (golden snapshot, structure validation, determinism at test layer) — but **no way for an external party to validate an EPB bundle without importing EZRA runtime code**. The artifact trust boundary was locked in shape and determinism, but not in **external verifiability**. Audits could not assert that a consumer could certify an EPB using only stdlib and the artifact itself.

**What would remain unsafe, brittle, or ungoverned if this refactor did not occur:**

- External consumers would have to trust EZRA’s own verification logic rather than recomputing hashes in isolation.
- No reproducible, stdlib-only certification path for archival or supply-chain use.
- No CI-enforced “consumer certification” step proving subprocess-isolated validation.
- No explicit reproducibility gate (emit → teardown → re-emit) at the test layer.

M25 introduces a **stdlib-only EPB certification utility** (`epb_certify.py`), **consumer-isolated certification tests** (subprocess, JSON summary), and a **reproducibility test** (directory teardown + re-emit, bundle hash match). All wired into CI. This is **artifact trust-boundary hardening** — no feature expansion, no API or schema changes, no new runtime dependencies.

---

## 2. Scope Definition

### In Scope

**Components/Modules Touched:**
- `src/ezra/tools/epb_certify.py` — Stdlib-only certification utility (NEW)
- `tests/contracts/test_epb_consumer_certification.py` — 6 certification/reproducibility tests (NEW)
- `.github/workflows/ci.yml` — EPB Consumer Certification step and summary section
- `docs/baselines/public_surface_snapshot.json` — Added `ezra.tools.epb_certify`
- `docs/ezra.md` — M25 row, Section 7A (planned M26–M32), Section 11 (v1.0.0 criteria), Artifact Trust Model
- `docs/milestones/M25/M25_plan.md`, `M25_run1.md`, `M25_toolcalls.md`

**Entrypoints Affected:** New CLI entry point: `python -m ezra.tools.epb_certify <bundle_path>` (stdout JSON, exit 0/1).

**Contracts/Interfaces Involved:** EPB bundle as directory of JSON files; certifier validates structure, per-file hashes, bundle hash, and hashes.json self-hash. No EPB schema change.

**CI Workflows/Gates Impacted:** Test job — new step “EPB Consumer Certification” and summary block (structure_validation, hash_integrity, bundle_hash, reproducibility).

### Out of Scope

**Areas Intentionally Untouched:** EPB emission logic, EPB schemas, plugin interfaces, zone subsystem, all existing runtime behavior.

**Features Explicitly Not Added:** Artifact signing (M26), detached metadata (M27), artifact-only distribution (M28), dependency upgrades, performance work.

**Work Deferred:** None.

---

## 3. Refactor Classification

### Change Type

**Boundary hardening + consumer certification** — New stdlib-only certification utility and contract tests at the EPB artifact boundary; reproducibility gate and CI step. No mechanical or semantic refactor of existing production code.

### Observability

**Externally Observable:**
- New public module `ezra.tools.epb_certify` and CLI `python -m ezra.tools.epb_certify`.
- CI Test job includes “EPB Consumer Certification” step and summary section.
- Public surface snapshot updated to include the new module (intentional).
- No change to EPB schema, emission output shape, or existing API.

---

## 4. Work Executed

**Key Actions:**
1. Added `src/ezra/tools/epb_certify.py` — canonicalization and hashing reimplemented in stdlib (8dp/6dp for zones), structure check, hash integrity and bundle hash verification, JSON result to stdout, exit 0/1.
2. Added `tests/contracts/test_epb_consumer_certification.py` with six tests: hash integrity (certifier agrees with emission), subprocess certification (exit 0 + JSON), reproducibility (emit to `a`, rmtree `a`, emit to `b`, same bundle hash), tampered bundle, missing file, invalid path.
3. Wired “EPB Consumer Certification” step and summary into `.github/workflows/ci.yml`.
4. Updated `docs/baselines/public_surface_snapshot.json` to include `ezra.tools.epb_certify`.
5. Updated `docs/ezra.md`: M25 completed row, Section 7A (planned M26–M32), Section 11 (v1.0.0 criteria), Artifact Trust Model subsection.
6. Resolved initial public surface freeze failure (snapshot update) and ruff line-length in certifier within the milestone.

**Counts:** New files: 2 (epb_certify.py, test_epb_consumer_certification.py). Modified: CI, snapshot, ezra.md, M25 docs, 2 test files (format only). New tests: 6. Test count: 262 passed, 4 skipped (256 baseline + 6 new).

**Migration Steps:** None.

**Functional Logic Changes:** None in existing emission or schema. New certification utility and tests only.

---

## 5. Invariants & Compatibility

### Declared Invariants (Must Not Change)

1. **EPB structure (M24)** — Required files and keys; verified by certifier structure check and tests.
2. **Determinism (M24)** — Identical inputs → identical outputs; verified by reproducibility test and existing harness.
3. **Artifact self-consistency** — hashes.json matches actual file digests; bundle hash matches recomputed value; verified by certifier and tests.
4. **Consumer-isolated validation** — Certification executable without EZRA runtime imports; verified by stdlib-only certifier and subprocess test.
5. **CI truthfulness** — No weakening of required checks; verified by workflow inventory and 9/9 passing.

### Compatibility Notes

- **Backward compatibility preserved:** Yes. New module and CLI only; no changes to existing API or EPB format.
- **Breaking changes introduced:** No.
- **Deprecations introduced:** No.

---

## 6. Validation & Evidence

| Evidence Type | Tool/Workflow | Result | Notes |
|---------------|---------------|--------|-------|
| Unit/contract tests | pytest | ✅ 262 passed, 4 skipped | 6 new certification tests |
| Coverage | pytest-cov | ✅ 95.90% (≥85%) | Unchanged from M24; tools omitted |
| Linting | Ruff | ✅ Pass | |
| Formatting | Ruff format | ✅ Pass | |
| Type checking | Mypy | ✅ Pass | |
| Security | Bandit, pip-audit, Gitleaks | ✅ Pass | 0 HIGH issues |
| Determinism | Workflow + contract tests | ✅ Pass | Workflow + reproducibility test |
| EPB Consumer Certification | pytest + CI step | ✅ Pass | Structure, hash integrity, bundle hash, reproducibility |
| CI (required jobs) | GitHub Actions | ✅ 9/9 passed | Run 22477994937 |

**Failures Encountered:** Initial run — public surface freeze (missing `ezra.tools.epb_certify` in snapshot) and certifier line length; resolved by snapshot update and ruff fix. CI: Dependency Review (SEC-001) failed; non-blocking, no action.

**Evidence that validation is meaningful:** Certifier recomputes hashes from disk using same canonicalization rules as emission; subprocess test proves module invocation and JSON shape; reproducibility test proves directory independence.

---

## 7. CI / Automation Impact

**Workflows Affected:** `.github/workflows/ci.yml` — Test job only.

**Checks Added:** EPB Consumer Certification step (runs `tests/contracts/test_epb_consumer_certification.py`); summary section (structure_validation, hash_integrity, bundle_hash, reproducibility).

**Enforcement Changes:** Stricter — certification step is required; no checks removed or weakened.

**Signal Quality:** CI run 22477994937: all 9/9 required jobs passed. Certification step and summary provide clear signal. No green-but-misleading path.

---

## 8. Issues, Exceptions, and Guardrails

**Issues Encountered:**
1. **Public surface freeze (pre-CI)** — Snapshot did not include `ezra.tools.epb_certify`. Resolved by adding module to `docs/baselines/public_surface_snapshot.json`. Guardrail: intentional surface expansion documented in milestone.
2. **Ruff E501 (certifier)** — Line length in error message. Resolved by splitting f-string. Guardrail: existing Ruff config unchanged.
3. **Dependency Review (CI)** — SEC-001; repo/org config. Non-blocking; carried forward. No M25 change.

**No new, untracked issues.**

---

## 9. Deferred Work

**Deferred Items:** None.

---

## 10. Governance Outcomes

**What is now provably true that was not provably true before:**

1. **EPB bundles are externally certifiable** — A consumer can validate structure, per-file hashes, bundle hash, and hashes.json self-hash using only Python stdlib and the bundle directory (no EZRA runtime imports).
2. **Certification is subprocess-isolated** — CI runs certification via `python -m ezra.tools.epb_certify`; exit code and JSON summary are asserted.
3. **Reproducibility is test-enforced** — Emit → rmtree → re-emit produces identical bundle hash; directory independence and determinism are verified.
4. **Artifact trust boundary is CI-enforced** — EPB Consumer Certification step blocks merge on failure; summary gives visibility.

**Governance posture:** Phase V release-lock artifact. EZRA now has schema lock, zone registry lock, determinism at workflow and test layer, snapshot-locked artifact surface, **stdlib-only certification tool**, **artifact self-consistency verification**, and **reproducibility enforcement** — an externally certifiable, reproducible artifact format.

---

## 11. Exit Criteria Evaluation

| Criterion | Status | Evidence |
|-----------|--------|----------|
| 100% EPB self-consistency verified | ✅ Met | Certifier + tests |
| Consumer certification runs in isolation | ✅ Met | Subprocess test |
| CI 9/9 required checks passing | ✅ Met | Run 22477994937 |
| Coverage unchanged or improved | ✅ Met | 95.90% (matches M24) |
| No invariant drift | ✅ Met | All declared invariants verified |
| Certification JSON stable | ✅ Met | Deterministic, stdout-only |
| Audit verdict 🟢 | ✅ Met | M25_audit.md |
| Tag v0.0.26-m25 | ✅ Met | Created and pushed |

---

## 12. Final Verdict

**Milestone objectives met. Refactor verified safe. Closed.**

M25 delivers stdlib-only EPB consumer certification, subprocess-isolated validation, and reproducibility enforcement at the artifact boundary. No runtime or schema changes; artifact trust model is externally verifiable and CI-enforced. Governance posture remains Phase V; CI evidence is complete. PR #26 merged; tag `v0.0.26-m25` created and pushed.

---

## 13. Authorized Next Step

**Next milestone:** M26 — Artifact Signing & Verification (when authorized).

**Constraints:** Maintain milestone boundary discipline; preserve all M25 invariants; continue behavior-preserving posture unless explicitly authorized.

---

## 14. Canonical References

**Commits:** `229ae1c` (main after merge), `6b24e1b` (feat M25), `521c69b` (docs M25_run1), `36af5f9` (docs ezra.md roadmap).

**Pull Request:** PR #26 — feat(M25): EPB Consumer Certification & Artifact Reproducibility Hardening

**CI Run:** https://github.com/m-cahill/ezra/actions/runs/22477994937

**Tag:** v0.0.26-m25

**Documents:** `docs/milestones/M25/M25_plan.md`, `M25_run1.md`, `M25_audit.md`, `M25_summary.md`, `M25_toolcalls.md`

**Baseline:** `v0.0.25-m24` (tag)
