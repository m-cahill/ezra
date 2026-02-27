# M28_run2 — CI Run Analysis

## 1. Workflow identity

| Field | Value |
|-------|--------|
| **Workflow** | CI |
| **Run ID** | 22508322567 |
| **URL** | https://github.com/m-cahill/ezra/actions/runs/22508322567 |
| **Trigger** | pull_request |
| **Branch** | m28-artifact-only-distribution |
| **PR** | [#30](https://github.com/m-cahill/ezra/pull/30) |
| **Started** | 2026-02-27T23:48:35Z |
| **Completed** | 2026-02-27T23:50:03Z |
| **Conclusion** | success |

---

## 2. Context

- **Milestone:** M28 — Artifact-Only Distribution Mode
- **Run purpose:** Verify post-fix test-isolation hardening for optional ML dependencies.
- **Posture:** Behavior-preserving; no architecture rollback.

---

## 3. Job inventory

| Job | Status | Notes |
|-----|--------|-------|
| Lint | ✅ success | |
| Type Check | ✅ success | |
| Test | ✅ success | Full suite passed after skip-when-missing hardening. |
| EPB Tools Minimal Environment | ✅ success | New M28 isolation gate passes. |
| Security Check | ✅ success | |
| Complexity Check | ✅ success | |
| SBOM Generation | ✅ success | |
| OpenSSF Scorecard | ✅ success | Informational/warn-first. |
| Documentation Build | ✅ success | |
| Determinism Check | ✅ success | Result: PASS; byte-identical bundles. |
| Hermetic Hash (Py 3.10/3.11/3.12) | ✅ success | All three matrix jobs passed. |
| Hermetic Reproducibility | ✅ success | Matrix hashes identical. |
| Dependency Review | ⚠️ failure (non-blocking) | Expected repo setting limitation; check is continue-on-error. |
| SLSA Provenance | skipped | Push-to-main/tags only. |
| Documentation Deploy | skipped | Push-to-main only. |

---

## 4. Test and coverage evidence

From Test job log (`M28_run2_test_job.log`):

- `collected 281 items`
- `253 passed, 28 skipped, 6 warnings`
- `Required test coverage of 85.0% reached. Total coverage: 85.69%`

Interpretation:

- Optional ML-dependent tests now skip when dependencies are absent (as intended).
- Required coverage gate is green in CI.

---

## 5. Determinism and hermetic evidence

From Determinism job log (`M28_run2_determinism.log`):

- `Result: PASS`
- `PASS: All bundles are byte-identical`

From Hermetic Reproducibility log (`M28_run2_hermetic.log`):

- `All matrix hashes are identical.`

Interpretation:

- No determinism regression from M28 or the follow-up test hardening.
- Cross-interpreter hermetic hash invariants are preserved.

---

## 6. M28 exit-criteria status (run2)

| Criterion | Status |
|-----------|--------|
| EPB tools import without runtime leakage | ✅ |
| Minimal environment gate passes | ✅ |
| Required CI gates pass for PR posture | ✅ |
| Test suite green without ML dependency creep | ✅ |
| Determinism preserved | ✅ |
| Hermetic reproducibility preserved | ✅ |
| Coverage gate preserved | ✅ |
| Public surface drift (unexpected) | ✅ none observed |

---

## 7. Conclusion

M28 is validated on CI after test-isolation hardening:

- Architecture remains intact (no rollback, no dependency creep).
- Artifact-only validation boundary is enforced and proven.
- Phase V governance signals (determinism/hermetic/coverage/required gates) are green.

