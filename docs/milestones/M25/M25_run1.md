# M25 Run 1 — CI / Workflow Run Analysis

**Milestone:** M25 — EPB Consumer Certification & Artifact Reproducibility Hardening  
**Posture:** Behavior-preserving (consumer certification harness only; no runtime/schema changes)  
**Run type:** Initial implementation + CI verification

---

## 1. Workflow identity

| Field        | Value |
|-------------|--------|
| Workflow    | CI (`.github/workflows/ci.yml`) |
| Run ID      | **22477994937** |
| URL         | https://github.com/m-cahill/ezra/actions/runs/22477994937 |
| Trigger     | pull_request |
| Branch      | `m25-epb-consumer-certification` |
| PR          | **#26** (m-cahill/ezra#26) |
| Conclusion  | success |
| Duration    | ~1m 25s |

---

## 2. Change context

- **Objective:** Add stdlib-only EPB certifier (`epb_certify.py`), consumer certification tests, reproducibility test (emit → rmtree → re-emit), and CI step.
- **Refactor target surface:** Artifact boundary (certification utility + contract tests); no change to EPB emission or schema.
- **Invariants:** EPB structure (M24), determinism (M24), new: artifact self-consistency, consumer-isolated validation.

---

## 3. Local verification (pre-CI)

| Check | Result | Notes |
|-------|--------|------|
| Pytest (all) | 262 passed, 4 skipped | 6 new tests in `test_epb_consumer_certification.py` |
| Coverage | 95.70% (≥85%) | `*/tools/*` omitted by config; rest of src unchanged |
| Ruff (lint) | Pass | `ruff check . --no-fix` |
| Ruff (format) | Pass | `ruff format --check .` |
| Mypy | Pass | `mypy src` |
| Public surface freeze | Pass | Snapshot updated to include `ezra.tools.epb_certify` |

---

## 4. Jobs / checks (CI inventory — Run 22477994937)

| Job / Check | Required? | Result | Notes |
|-------------|-----------|--------|-------|
| Lint | Yes | ✓ Pass | 27s |
| Type Check | Yes | ✓ Pass | 25s |
| Test | Yes | ✓ Pass | 48s; 262 passed, 4 skipped; coverage 95.90% |
| Security Check | Yes | ✓ Pass | 32s |
| SBOM Generation | Yes | ✓ Pass | 36s |
| Complexity Check | Yes | ✓ Pass | 25s |
| Determinism Check | Yes | ✓ Pass | 28s |
| Documentation Build | Yes | ✓ Pass | 18s |
| Dependency Review | continue-on-error | ✗ Fail | SEC-001 (repo/org config; not blocking) |
| OpenSSF Scorecard | continue-on-error | ✓ Pass | 12s |
| SLSA Provenance | Conditional (push/tag) | Skipped | PR trigger |
| Documentation Deploy | Conditional (push/main) | Skipped | PR trigger |

**EPB Consumer Certification step (inside Test job):** 6 tests passed in 1.50s. Outputs: structure_validation=PASS, hash_integrity=PASS, bundle_hash=PASS, reproducibility=PASS.

---

## 5. Certification JSON output (stability)

Certifier output shape (success):

```json
{
  "bundle_hash_valid": true,
  "deterministic": true,
  "epb_version": "1.0.0",
  "hash_integrity_valid": true,
  "structure_valid": true,
  "valid": true
}
```

- Emitted to stdout only; exit code 0. On failure: `valid: false`, `errors` array, exit code 1.
- Deterministic for a given bundle path (no timestamps in output).

---

## 6. Failures encountered

- **Local:** None. Public surface freeze failed initially until `docs/baselines/public_surface_snapshot.json` was updated to include `ezra.tools.epb_certify` (in-scope for M25).
- **CI:** Dependency Review job failed (Dependency graph / GitHub Advanced Security not enabled). Known SEC-001; `continue-on-error: true`. All **9/9 required (merge-blocking) checks passed**. No corrective action required for M25.

---

## 7. Delta summary

| Item | Delta |
|------|--------|
| New files | `src/ezra/tools/epb_certify.py`, `tests/contracts/test_epb_consumer_certification.py` |
| Modified | `.github/workflows/ci.yml`, `docs/baselines/public_surface_snapshot.json`, `docs/milestones/M25/*` |
| Test count | 256 → 262 (+6) |
| Coverage (CI) | **95.90%** (tools omitted; matches M24) |

---

## 8. Verdict

**Verdict:** CI run 22477994937 completed successfully. All 9/9 required checks passed. EPB Consumer Certification step ran and reported PASS for structure validation, hash integrity, bundle hash, and reproducibility. Coverage 95.90% (unchanged from M24). Dependency Review failure is known infra (SEC-001) and non-blocking.

**Outcome:** ✅ **Merge approved.**

---

## 9. Exit criteria (M25)

| Criterion | Status |
|-----------|--------|
| 100% EPB self-consistency verified | Yes (tests + certifier) |
| Consumer certification runs in isolation | Yes (subprocess test) |
| CI 9/9 required checks passing | ✅ Met (Run 22477994937) |
| Coverage unchanged or improved | ✅ 95.90% (matches M24) |
| No invariant drift | Yes |
| Certification JSON output stable | Yes (deterministic, stdout-only) |

---

**CI run ID:** 22477994937  
**PR:** #26  
**Coverage (CI):** 95.90% (M24 baseline 95.90%; tools excluded by design.)

---

## 10. Next actions

| Action | Owner | Scope |
|--------|--------|--------|
| Merge PR #26 | Human | After approval |
| Tag `v0.0.26-m25` | Human | Post-merge |
| Generate M25_audit.md, M25_summary.md | Cursor / Human | After CI green confirmed |
| Update docs/ezra.md milestone table | Cursor / Human | Closeout |
