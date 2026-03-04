# M28_run1 — CI Run Analysis

## 1. Workflow identity

| Field | Value |
|-------|--------|
| **Workflow** | CI |
| **Run ID** | 22507799104 |
| **URL** | https://github.com/m-cahill/ezra/actions/runs/22507799104 |
| **Trigger** | pull_request |
| **Branch** | m28-artifact-only-distribution |
| **Display title** | M28: Artifact-Only Distribution Mode |
| **PR** | [#30](https://github.com/m-cahill/ezra/pull/30) |
| **Started** | 2026-02-27T23:26:22Z |
| **Completed** | 2026-02-27T23:27:07Z |
| **Conclusion** | failure |

---

## 2. Change context

| Field | Value |
|-------|--------|
| **Milestone** | M28 — Artifact-Only Distribution Mode |
| **Intent** | Physically isolate EPB validation tooling into `ezra.epb_tools`; runtime-independent artifact validation; preserve backward CLI via wrappers. |
| **Refactor target** | `src/ezra/epb_tools/` (new), `src/ezra/tools/` (wrappers), `tests/contracts/test_epb_tools_*.py`, CI job "EPB Tools Minimal Environment", public surface snapshot. |
| **Posture** | Behavior-preserving |
| **Run type** | First run after PR open |

---

## 3. Job inventory

| Job | Required | Pass/Fail | Duration | Notes |
|-----|----------|-----------|----------|--------|
| Lint | Yes | ✅ success | 23s | Ruff + pydocstyle |
| Type Check | Yes | ✅ success | 25s | Mypy |
| **EPB Tools Minimal Environment** | Yes | ✅ success | 13s | **New in M28.** `pip install . pytest` → `pytest tests/contracts/test_epb_tools_*.py`. Isolation proven. |
| Test | Yes | ❌ failure | 40s | Pytest failed; see §5. Downstream steps skipped. |
| Security Check | Yes | ✅ success | 30s | Bandit, pip-audit, gitleaks |
| Complexity Check | Yes | ✅ success | 28s | Radon |
| SBOM Generation | Yes | ✅ success | 38s | CycloneDX |
| OpenSSF Scorecard | No (warn-first) | ✅ success | 14s | Informational |
| Documentation Build | Yes | ✅ success | 16s | Sphinx |
| Dependency Review | No (continue-on-error) | ❌ failure | 7s | Advanced Security not enabled; known non-blocking. |
| SLSA Provenance | Conditional (push main/tag) | skipped | — | PR run |
| Documentation Deploy | Conditional (push main) | skipped | — | PR run |
| Determinism Check | Yes | skipped | — | `needs: test` — Test failed |
| Hermetic Hash (Py 3.10/3.11/3.12) | Yes | skipped | — | `needs: test` |
| Hermetic Reproducibility | Yes | skipped | — | `needs: hermetic-hash-matrix` |

---

## 4. M28-specific signal

- **EPB Tools Minimal Environment:** ✅ **PASSED.** `ezra.epb_tools` imports without loading `ezra.core`, `ezra.plugins`, `torch`, or `easyocr`; isolation test passed on CI.
- **Contract tests (in Test job, before failure):** All 21 EPB contract tests **PASSED**, including:
  - `test_epb_tools_import_surface_no_runtime_or_ml`
  - All consumer certification, artifact signing, and cert metadata tests (in-process and subprocess).
- **Public surface:** Snapshot includes +3 modules (`ezra.epb_tools.*`); wrappers remain under `ezra.tools`. No unexpected surface change.
- **Hermetic matrix / Determinism:** Not run (blocked by Test failure). No evidence of regression from M28.

---

## 5. Test job failure analysis

**Failed step:** Pytest with coverage (exit code 2).

**Pytest summary:** 35 failed, 242 passed, 4 skipped, 6 warnings (8.58s).  
**Coverage:** 83.23% (fail-under 85%). Coverage step was skipped because pytest failed.

**Root cause:** **Environment / test isolation — not M28.** CI installs `.[dev]` but does **not** install `.[easyocr]` or torch. Failures are:

| Failing area | Count | Cause |
|-------------|--------|--------|
| test_easyocr_adapter | 10 | `ImportError: EasyOCR is not installed`. Patch of `easyocr` does not prevent adapter from importing at use time. |
| test_easyocr_plugin | 6 | Same as above. |
| test_plugin_registry | 14 | `get_plugin("easyocr")` (or validation touching easyocr) triggers adapter load → ImportError. |
| test_parity_unit | 4 | Manifest environment validation expects torch/easyocr or specific error text; env differs. |
| test_zone_contract | 1 | `test_i3_registry_frozen_prevents_mutation` — likely order/env sensitive. |

**Conclusion:** No failure is in `ezra.epb_tools` or in EPB contract tests. Fix requires test isolation (skip or mock when EasyOCR/torch absent), not M28 code or architecture change.

---

## 6. Pre-merge checklist (M28_run1)

| Criterion | Status | Note |
|-----------|--------|------|
| All required CI jobs passing | ❌ | Test failed; Determinism/Hermetic skipped. |
| EPB Tools Minimal Environment passing | ✅ | 13s, isolation verified. |
| Isolation test passing | ✅ | In Test job and in minimal job. |
| Contract tests passing | ✅ | All 21 EPB contract tests passed. |
| Public surface snapshot match | ✅ | +3 modules only; wrappers present. |
| Coverage ≥ 95% (or no drop) | — | Not reported (pytest failed); run showed 83.23%. |
| Hermetic matrix passing | — | Skipped (Test blocked). |

---

## 7. Conclusions and next steps

- **M28 implementation:** Architecture and behavior are correct. EPB tools are isolated, wrappers preserved, new CI guardrail passes.
- **Blocker:** Test job fails due to EasyOCR/torch test isolation in CI, not due to M28.
- **Next step:** Adjust test isolation (e.g. skip or mock when EasyOCR/torch not installed) so the Test job passes on CI; re-run to confirm Determinism, Hermetic, and coverage. No M28 code changes required for that.

---

## 8. Artifacts

- **Run:** https://github.com/m-cahill/ezra/actions/runs/22507799104  
- **PR:** https://github.com/m-cahill/ezra/pull/30  
- **Failed log (Pytest):** `gh run view 22507799104 --log-failed`
