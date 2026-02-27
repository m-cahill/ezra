# M29 Run 1 — CI / Workflow Run Analysis

**Milestone:** M29 — Hermetic Reproducibility Gate  
**Posture:** Behavior-preserving (CI-only hardening; no schema/emission/runtime changes)  
**Run type:** Initial implementation + CI verification

---

## 1. Workflow identity

| Field | Value |
|------|-------|
| Workflow | CI (`.github/workflows/ci.yml`) |
| Run ID | **22504550465** (final green run) |
| URL | https://github.com/m-cahill/ezra/actions/runs/22504550465 |
| Trigger | pull_request |
| Branch | `m29-hermetic-reproducibility` |
| PR | **#28** (m-cahill/ezra#28) |
| Conclusion | success |
| Duration | ~1m 07s |

---

## 2. Change context

- **Objective:** Enforce cross-interpreter hermetic reproducibility for canonical EPB bundle hash across Python 3.10/3.11/3.12.
- **Refactor target surface:** CI workflow only (`.github/workflows/ci.yml`), milestone documentation.
- **Invariants:** EPB structure (M24), determinism (M24/M25), artifact self-consistency (M25), signature validity (M26), and new hermetic equivalence gate.

---

## 3. Local verification (pre-CI)

| Check | Result | Notes |
|------|--------|------|
| Focused contract tests | 12 passed | `test_epb_consumer_certification.py` + `test_epb_artifact_signing.py` |
| Scope safety | Pass | No runtime/schema/canonicalization code edits |

---

## 4. Jobs / checks (CI Run 22504550465)

| Job / Check | Required? | Result | Notes |
|------------|-----------|--------|------|
| Lint | Yes | Pass | |
| Type Check | Yes | Pass | |
| Test | Yes | Pass | 268 passed, 4 skipped; coverage 95.90% |
| Security Check | Yes | Pass | |
| SBOM Generation | Yes | Pass | |
| Complexity Check | Yes | Pass | |
| Determinism Check | Yes | Pass | |
| Hermetic Hash (Py 3.10) | Yes | Pass | Artifact: `hermetic-hash-py3.10` |
| Hermetic Hash (Py 3.11) | Yes | Pass | Artifact: `hermetic-hash-py3.11` |
| Hermetic Hash (Py 3.12) | Yes | Pass | Artifact: `hermetic-hash-py3.12` |
| Hermetic Reproducibility | Yes | Pass | Hash comparison gate |
| Documentation Build | Yes | Pass | |
| Dependency Review | continue-on-error | Fail | SEC-001 infra-only (non-blocking) |
| OpenSSF Scorecard | continue-on-error | Pass | |
| SLSA Provenance | Conditional | Skipped | PR trigger |
| Documentation Deploy | Conditional | Skipped | PR trigger |

---

## 5. Hermetic matrix evidence

From `Hermetic Reproducibility` job logs:

- `hermetic-hash-py3.10`: `c186777c33b7b7b9d11540bda7398efd0dfb085143506513a4ce87836c6ac7c2`
- `hermetic-hash-py3.11`: `c186777c33b7b7b9d11540bda7398efd0dfb085143506513a4ce87836c6ac7c2`
- `hermetic-hash-py3.12`: `c186777c33b7b7b9d11540bda7398efd0dfb085143506513a4ce87836c6ac7c2`

Result: all hashes identical; divergence gate not triggered.

---

## 6. Failures encountered and fix path

Earlier runs failed before the final green run:

1. **Run 22504290359:** Python 3.10 install failed (`requires-python >=3.11`) and matrix artifact naming collisions.
2. **Run 22504361016:** same 3.10 floor issue remained.
3. **Run 22504428388:** full test matrix on 3.10 failed due `datetime.UTC` (Python 3.11+ symbol).

Final fix:

- Kept full `Test` job on Python 3.11 (existing posture).
- Added dedicated hermetic hash matrix job for 3.10/3.11/3.12 using stdlib-only fixture + hash path.
- Added required comparison job to fail on any hash mismatch.
- Preserved all existing required checks (no weakening).

---

## 7. Coverage / test delta

| Metric | Value |
|-------|-------|
| Test count (CI) | 268 passed, 4 skipped (unchanged) |
| Coverage (CI) | **95.90%** (unchanged from M25 baseline) |
| Runtime behavior | Unchanged |

---

## 8. Verdict

**Verdict:** ✅ M29 CI gate is functioning as intended. Canonical bundle hash equivalence is now enforced across Python 3.10/3.11/3.12, with explicit artifact evidence and fail-fast comparison behavior.

**CI run ID:** 22504550465  
**PR:** #28  
**Hermetic hash (all matrix jobs):** `c186777c33b7b7b9d11540bda7398efd0dfb085143506513a4ce87836c6ac7c2`
