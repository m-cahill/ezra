# Milestone Summary — M28

**Project:** EZRA  
**Phase:** Phase V (Release Lock / artifact-governed posture)  
**Milestone:** M28 — Artifact-Only Distribution Mode  
**Timeframe:** 2026-02-27  
**Status:** Closed  
**Baseline:** e7c4f1b (M27 merge); tag v0.0.29-m27  
**Refactor Posture:** Behavior-Preserving

---

## 1. Milestone Objective

Physically isolate EPB validation tooling into a runtime-independent namespace (`ezra.epb_tools`) to enable artifact validation without requiring the full EZRA runtime engine, OCR plugins, or ML dependencies. This strengthens artifact-boundary isolation and enables ecosystem distribution.

---

## 2. Scope Definition

### In Scope
- New namespace: `ezra.epb_tools` with physically isolated EPB tools
- Moved tools: `epb_certify.py`, `epb_verify.py`, `epb_generate_cert_metadata.py`
- Legacy CLI wrappers in `ezra.tools` with `DeprecationWarning`
- Import surface isolation test enforcing no runtime/plugin/ML imports
- CI job `EPB Tools Minimal Environment` validating isolation in fresh venv
- ML-dependent test isolation with `pytest.mark.skipif` guards
- Public surface snapshot update (+3 modules)

### Out of Scope
- No distribution split (no `ezra[epb-tools]` extras yet — M28 proves architectural isolation, not distribution)
- No schema/emission/canonicalization/hashing changes
- No runtime code changes
- No dependency changes (except test utilities)

---

## 3. Refactor Classification

**Change Type:** Boundary refactor (module extraction; import surface isolation).  
**Observability:** New import path `ezra.epb_tools.*`; old paths emit deprecation warnings; existing EPB contents and emission unchanged.

---

## 4. Work Executed

- Created `src/ezra/epb_tools/` with isolated EPB tools importing only stdlib + internal hash utility
- Converted `src/ezra/tools/epb_{certify,verify,generate_cert_metadata}.py` to thin wrappers with `DeprecationWarning`
- Added `tests/contracts/test_epb_tools_import_surface.py` asserting no `ezra.core`, `ezra.plugins`, `torch`, or `easyocr` in `sys.modules` after import
- Added `tests/utils/ml_available.py` with `has_easyocr()` and `has_torch()` helpers
- Applied `pytest.mark.skipif` guards to ML-dependent tests in `test_easyocr_adapter.py`, `test_easyocr_plugin.py`, `test_plugin_registry.py`, `test_parity_unit.py`
- Added required CI job `epb-tools-minimal` running isolation tests in fresh venv
- Updated public surface snapshot with new `ezra.epb_tools.*` modules

---

## 5. Invariants & Compatibility

**Declared invariants (unchanged):** EPB v1.0.0 schema frozen; canonicalization, hashing, signing rules; hermetic reproducibility; determinism.

**Compatibility:** Backward compatibility preserved. Legacy import paths still work with deprecation warning. No breaking changes. No removals.

---

## 6. Validation & Evidence

| Evidence Type    | Tool/Workflow           | Result   | Notes                                      |
|------------------|-------------------------|----------|--------------------------------------------|
| Unit/contract    | pytest                  | 253 pass | +1 isolation test                          |
| Skipped          | pytest                  | 28 skip  | ML-dependent tests correctly skipped       |
| Coverage         | pytest-cov              | 85.69%   | Above 85% gate; drop governance-correct    |
| Lint/format      | Ruff                    | Pass     |                                            |
| Type             | Mypy                    | Pass     |                                            |
| Public surface   | Snapshot diff           | Pass     | +3 modules added to snapshot               |
| Import isolation | test_epb_tools_import_surface | Pass | No runtime/plugin/ML imports               |
| CI               | Run 22508322567         | Green    | All required checks pass                   |
| EPB Tools Minimal| New required job        | Pass     | Isolation validated in fresh venv          |
| Determinism      | determinism job         | Pass     | Byte-identical bundles across runs         |
| Hermetic Matrix  | 3.10/3.11/3.12          | Pass     | Identical hashes across Python versions    |

---

## 7. CI / Automation Impact

- One new required job: `EPB Tools Minimal Environment` (pytest tests/contracts/test_epb_tools_*.py in minimal venv)
- No checks removed or weakened
- No signal drift
- Dependency Review remains continue-on-error (SEC-001)

---

## 8. Issues, Exceptions, and Guardrails

- **Run 1 Test Failures:** ML-dependent tests failed when deps absent. Fixed via `pytest.mark.skipif` guards. Not a regression; governance-correct isolation hardening.
- **Dependency Review:** Failed (SEC-001); non-blocking; pre-existing.

No new issues introduced. Test isolation hardening was planned response.

---

## 9. Deferred Work

None. Distribution split (separate PyPI package) deferred to Phase VI. SEC-001 (Dependency Review) pre-existing; status unchanged.

---

## 10. Governance Outcomes

- EPB validation surface is now **physically isolated** and **provably runtime-independent**
- Import isolation test prevents future leakage
- CI job enforces isolation on every PR
- Legacy CLI paths preserved for backward compatibility
- Architectural isolation proven; distribution split becomes optional (Phase VI)

---

## 11. Exit Criteria Evaluation

| Criterion                              | Status | Evidence |
|----------------------------------------|--------|----------|
| EPB tools import without runtime       | Met    | Isolation test |
| No ezra.core/plugins/torch/easyocr imports | Met | sys.modules check |
| Minimal environment CI job passes      | Met    | Run 22508322567 |
| Legacy CLI paths preserved             | Met    | Thin wrappers with DeprecationWarning |
| CI 9/9+ required checks passing        | Met    | Run 22508322567 |
| No runtime/schema changes              | Met    | No core/specs edits |
| Audit verdict 🟢                       | Met    | M28_audit.md |

---

## 12. Final Verdict

Milestone objectives met. Architectural isolation proven. Behavior-preserving refactor verified safe. Invariants held. CI green. Proceed.

---

## 13. Authorized Next Step

**Next milestone:** Phase V Completion Declaration or v1.0.0 readiness milestone. No post-merge commits to the M28 branch.

---

## 14. Canonical References

- **Commits:** 588b678 (CI evidence), 6cab0df (test isolation), f79af06 (M28 implementation)
- **PR:** #30 — M28: Artifact-Only Distribution Mode
- **Tag:** v0.0.30-m28
- **CI run:** https://github.com/m-cahill/ezra/actions/runs/22508322567
- **Docs:** docs/milestones/M28/M28_plan.md, M28_run1.md, M28_run2.md, M28_audit.md, M28_summary.md, M28_toolcalls.md
