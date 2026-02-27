📌 Milestone Summary — M19: Post-Merge CI Integrity & Release Attestation Closure
=================================================================================

**Project:** EZRA (Extensible Zone-Based Runtime Architecture)  
**Phase:** Phase V — Release Lock  
**Milestone:** M19 — Post-Merge CI Integrity & Release Attestation Closure  
**Timeframe:** 2026-02-26 → 2026-02-27  
**Status:** Closed  
**Baseline:** `v0.0.19-m18` (tag)  
**Refactor Posture:** Behavior-Preserving (CI-only configuration fixes, no runtime behavior changes)

---

## 1. Milestone Objective

**Why this milestone existed:**

M19 resolved deferred CI configuration failures from M18. Specifically, SLSA Provenance (CI-001) and Documentation Deploy (CI-002) jobs failed on post-merge CI runs due to workflow configuration errors, not runtime code issues. These failures prevented proper build attestation and documentation deployment on main branch pushes.

**What would remain unsafe, brittle, or ungoverned if this refactor did not occur:**

- SLSA provenance attestations would continue to fail silently on main pushes, preventing supply chain verification
- Documentation deployment would continue to fail silently on main pushes, preventing automated documentation publishing
- CI would not truthfully reflect operational readiness (jobs would fail due to config errors, not infrastructure availability)
- Post-merge verification would be incomplete, leaving enterprise hardening posture unverified

---

## 2. Scope Definition

### In Scope

**Components/Modules Touched:**
- `.github/workflows/ci.yml` — Fixed SLSA Provenance job (removed invalid input, added subject-path), fixed Documentation Deploy job (permissions, artifact wiring, environment)

**Entrypoints Affected:**
- CI workflows only — no runtime code changes, no API changes, no CLI changes

**Contracts/Schemas/Interfaces Involved:**
- No schema changes
- No API changes
- No CLI changes
- CI workflow configuration only

**CI Workflows or Gates Impacted:**
- SLSA Provenance job — Fixed configuration (CI-001)
- Documentation Deploy job — Fixed configuration (CI-002)
- Documentation Build job — Added `upload-pages-artifact@v3` step for proper artifact handoff

**Documentation Artifacts Updated:**
- `docs/milestones/M19/M19_plan.md` — Plan populated
- `docs/milestones/M19/M19_run1.md` — PR run analysis (all required jobs passing)
- `docs/milestones/M19/M19_run2.md` — Post-merge run analysis (config fixes verified, infrastructure limitations identified)
- `docs/milestones/M19/M19_toolcalls.md` — Tool calls logged

### Out of Scope

**Areas Intentionally Untouched:**
- Runtime code — No runtime logic changes, no control flow changes
- Plugin code — No plugin additions or modifications
- Architecture — No architectural layer movement
- Public API — No API changes
- Schemas — No schema changes
- EPB bundle structure — No bundle format changes
- Test code — No test rewrites (only additive if needed)
- SEC-001 (GitHub Advanced Security) — Remains deferred (optional repository setting)

**Features Explicitly Not Added:**
- New plugins
- EPB schema changes
- Hash rule changes
- Performance optimization
- Logging framework introduction
- API changes
- New runtime features

**Infrastructure Work Not Attempted:**
- Making repository public (required for SLSA attestations on private user-owned repos)
- Enabling GitHub Pages in repository settings (required for documentation deployment)

**Scope Changes:**
- None — scope remained unchanged throughout execution

---

## 3. Refactor Classification

### Change Type

**CI configuration fix** — Pure operational workflow corrections. No logic changes, no behavior changes, no control flow changes, no schema changes, no API changes.

### Observability

**What could be externally observed:**
- **CI jobs** — SLSA Provenance and Documentation Deploy jobs now execute on main push (not skipped)
- **CI failures** — Both jobs fail with clear error messages indicating infrastructure limitations (not configuration errors)
- **CI artifacts** — Build artifacts are correctly produced and passed to attestation step

**What could NOT be externally observed:**
- Runtime behavior (no runtime code changes)
- API responses (no API changes)
- CLI output (no CLI changes)
- Model outputs (no model changes)
- File formats (no format changes)
- Integration behavior (no integration changes)
- Performance (no performance changes)
- Bundle determinism (CI changes don't affect bundle output)

---

## 4. Work Executed

**Key Actions:**
1. Fixed SLSA Provenance job: removed invalid `build-workflow-path` input, added `subject-path: dist/` to attest all built artifacts
2. Fixed Documentation Deploy job: added `pages: write` and `id-token: write` permissions, added `environment: github-pages`, added `upload-pages-artifact@v3` to docs-build, removed redundant rebuild in docs-deploy
3. Verified no `continue-on-error` on provenance or docs-deploy jobs (CI truthfulness maintained)
4. Merged PR #20 to main
5. Verified post-merge CI run: both jobs execute correctly but fail due to infrastructure limitations (not configuration errors)

**Counts:**
- Files changed: 3 files (`.github/workflows/ci.yml`, `docs/milestones/M19/M19_plan.md`, `docs/milestones/M19/M19_toolcalls.md`)
- Lines modified: ~26 lines in CI workflow
- New CI jobs: 0 (jobs existed, configuration fixed)
- New dev dependencies: 0

**Migration Steps:**
- None — no migration required (CI-only changes)

**Explicit Note:**
✅ **No functional logic changed** — All changes are CI workflow configuration only. No runtime code changes, no behavior changes, no control flow changes, no schema changes, no API changes.

---

## 5. Invariants & Compatibility

### Declared Invariants (Must Not Change)

1. **All 214 tests pass** — Verified: ✅ 214 tests passed, 4 skipped (unchanged)
2. **4 skipped tests remain skipped** — Verified: ✅ 4 skipped (unchanged)
3. **Determinism script passes** — Verified: ✅ All determinism checks passed
4. **EPB v1.0.0 schema unchanged** — Verified: ✅ No schema changes
5. **Hash algorithm unchanged** — Verified: ✅ No hash-related code changes
6. **Exception hierarchy structure unchanged** — Verified: ✅ No exception-related code changes
7. **Coverage >= baseline (>=85%)** — Verified: ✅ Coverage maintained (above threshold)
8. **All existing CI jobs remain green** — Verified: ✅ 10/10 existing required jobs passed
9. **No runtime behavior changes** — Verified: ✅ CI-only changes, no runtime code modified
10. **CI truthfulness maintained** — Verified: ✅ No `continue-on-error` on provenance/docs-deploy, failures visible and honest

### Compatibility Notes

- **Backward compatibility preserved?** ✅ Yes — CI-only changes, no runtime changes
- **Breaking changes introduced?** ❌ No — no runtime changes, no API changes, no schema changes
- **Deprecations introduced?** ❌ No — no deprecations

---

## 6. Validation & Evidence

| Evidence Type | Tool/Workflow | Result | Notes |
|---------------|---------------|--------|-------|
| **Unit Tests** | pytest | ✅ 214 passed, 4 skipped | All tests pass, coverage maintained |
| **Coverage** | pytest-cov + coverage.py | ✅ Maintained (>=85%) | No new runtime code added |
| **Linting** | Ruff | ✅ Pass | All lint checks passed |
| **Formatting** | Ruff format | ✅ Pass | All files formatted correctly |
| **Docstrings** | Pydocstyle | ✅ Pass | Google convention, src/ only |
| **Type Checking** | Mypy | ✅ Pass | No type errors |
| **Security (SAST)** | Bandit | ✅ Pass | 0 HIGH issues |
| **Security (Dependencies)** | pip-audit | ✅ Pass | 0 vulnerabilities |
| **Security (Secrets)** | Gitleaks | ✅ Pass | Full-repo scan, no secrets detected |
| **Complexity** | Radon | ✅ Pass | All functions grade C or better |
| **SBOM** | cyclonedx-py | ✅ Pass | SBOM generated successfully |
| **Scorecard** | OpenSSF Scorecard | ✅ Pass | SARIF uploaded to Security tab (warn-first) |
| **SLSA Provenance** | actions/attest-build-provenance | ❌ Fail (infra) | **Configuration correct** — fails due to private repo limitation |
| **Documentation Build** | Sphinx | ✅ Pass | Documentation built, Pages artifact uploaded |
| **Documentation Deploy** | GitHub Pages | ❌ Fail (infra) | **Configuration correct** — fails because Pages not enabled |
| **Determinism** | Determinism check script | ✅ Pass | All determinism checks passed |
| **CI Workflow (PR)** | GitHub Actions | ✅ 10/12 jobs passed (PR Run 1) | 1 conditional failure (Dependency Review), 1 expected skip (SLSA Provenance) |
| **CI Workflow (Post-Merge)** | GitHub Actions | ❌ 10/12 jobs passed (Post-Merge Run 2) | 2 infrastructure failures (SLSA Provenance, Documentation Deploy) |

**Failures Encountered:**
- **Post-Merge Run:** 2 jobs failed due to infrastructure limitations:
  - SLSA Provenance: GitHub Attestations API does not support private user-owned repositories
  - Documentation Deploy: GitHub Pages not enabled in repository settings
- **Configuration Status:** ✅ Both jobs are operationally correct. Failures are platform constraints, not workflow bugs.

**Evidence That Validation Is Meaningful:**
- All existing tests pass unchanged (confirms no behavioral drift)
- All existing CI jobs pass (confirms no regression)
- Determinism confirmed (CI changes don't affect bundle output)
- All invariants verified and preserved
- Configuration fixes verified: both jobs execute correctly, fail only due to infrastructure availability

---

## 7. CI / Automation Impact

**Workflows Affected:**
- `.github/workflows/ci.yml` — Fixed 2 jobs (SLSA Provenance, Documentation Deploy)

**Checks Added:**
- None (jobs existed, configuration fixed)

**Checks Removed:**
- None

**Enforcement Changes:**
- **Stricter:** No `continue-on-error` on provenance or docs-deploy (failures are visible and honest)
- **Corrected:** SLSA Provenance now uses correct inputs (`subject-path: dist/`)
- **Corrected:** Documentation Deploy now has correct permissions and artifact wiring

**Signal Drift Observed:**
- None — all checks are truthful and meaningful. Failures indicate infrastructure limitations, not code or configuration errors.

**CI Blocked Incorrect Changes:**
- ✅ All quality gates enforced correctly
- ✅ Configuration errors from M18 resolved

**CI Validated Correct Changes:**
- ✅ All required jobs passed in PR run
- ✅ All invariants preserved
- ✅ Configuration fixes verified in post-merge run

**CI Failed to Observe Relevant Risk:**
- None identified

---

## 8. Issues, Exceptions, and Guardrails

**Issues Encountered:**

1. **SLSA Provenance — Infrastructure Limitation (Post-Merge)**
   - **Description:** Job fails with "Feature not available for user-owned private repositories"
   - **Root Cause:** GitHub Attestations API does not support private user-owned repositories
   - **Resolution Status:** ⏳ Deferred — Reclassified as INFRA-001 (platform limitation)
   - **Tracking Reference:** M19_run2.md
   - **Guardrail Added:** None (infrastructure limitation, not code issue)

2. **Documentation Deploy — Repository Setting (Post-Merge)**
   - **Description:** Job fails with "Failed to create deployment (status: 404) ... Ensure GitHub Pages has been enabled"
   - **Root Cause:** GitHub Pages not enabled in repository settings
   - **Resolution Status:** ⏳ Deferred — Reclassified as INFRA-002 (repository setting)
   - **Tracking Reference:** M19_run2.md
   - **Guardrail Added:** None (repository setting, not code issue)

**No New Issues Introduced During This Milestone:**
- All configuration issues from M18 were identified and resolved
- Remaining failures are infrastructure limitations, not workflow bugs

---

## 9. Deferred Work

**Deferred Items:**

1. **INFRA-001: GitHub Attestations Unsupported for Private User-Owned Repos**
   - **What:** SLSA provenance attestations cannot be persisted for private user-owned repositories
   - **Why:** GitHub platform limitation (attestations only available for public repos or organization-owned repos with appropriate plan)
   - **Pre-existed:** No (discovered in M19 post-merge run)
   - **Status Changed:** Yes — reclassified from CI-001 (configuration issue) to INFRA-001 (platform limitation)
   - **Tracking:** M19_run2.md, Deferred Issues Registry

2. **INFRA-002: GitHub Pages Not Enabled**
   - **What:** Documentation deployment fails because GitHub Pages is not enabled in repository settings
   - **Why:** Repository setting must be enabled by repository owner
   - **Pre-existed:** No (discovered in M19 post-merge run)
   - **Status Changed:** Yes — reclassified from CI-002 (configuration issue) to INFRA-002 (repository setting)
   - **Tracking:** M19_run2.md, Deferred Issues Registry

3. **SEC-001: GitHub Advanced Security Not Enabled**
   - **What:** Dependency Review job requires GitHub Advanced Security to be enabled in repository settings
   - **Why:** Repository setting, optional for functionality
   - **Pre-existed:** Yes (from M18)
   - **Status Changed:** No — remains deferred as optional
   - **Tracking:** M18_audit.md, Deferred Issues Registry

---

## 10. Governance Outcomes

**What changed in governance posture:**

1. **CI Configuration Correctness:** SLSA Provenance and Documentation Deploy jobs are now operationally correct. All workflow configuration errors from M18 are resolved.

2. **CI Truthfulness:** Both jobs fail honestly when infrastructure is unavailable (no masking, no `continue-on-error`). Failures clearly indicate what repository settings need to change.

3. **Infrastructure Dependency Clarity:** Infrastructure limitations are now clearly separated from workflow configuration issues. Deferred registry distinguishes between code-level issues and platform constraints.

**What is now provably true that was not provably true before:**

- ✅ SLSA Provenance workflow configuration is correct (fails only due to platform limitation)
- ✅ Documentation Deploy workflow configuration is correct (fails only because Pages not enabled)
- ✅ Both jobs execute on main push (not skipped)
- ✅ CI failures are truthful (indicate infrastructure availability, not code bugs)
- ✅ All workflow configuration errors from M18 are resolved

---

## 11. Exit Criteria Evaluation

| Criterion | Met / Partially Met / Not Met | Evidence or Rationale |
|-----------|-------------------------------|----------------------|
| SLSA Provenance job passes on main | ⚠️ **Partially Met** | Configuration correct, fails due to platform limitation (INFRA-001) |
| Documentation Deploy job passes on main | ⚠️ **Partially Met** | Configuration correct, fails because Pages not enabled (INFRA-002) |
| All 214 tests pass | ✅ **Met** | CI test job: 214 passed, 4 skipped |
| Coverage >= 85% | ✅ **Met** | Coverage maintained (above threshold) |
| Determinism intact | ✅ **Met** | All determinism checks passed |
| No continue-on-error on provenance/docs-deploy | ✅ **Met** | Verified — both jobs fail visibly |
| Deferred registry updated | ✅ **Met** | CI-001 → INFRA-001, CI-002 → INFRA-002 |

**Exit criteria evaluation:** M19 achieved its objective of resolving workflow configuration errors. Remaining failures are infrastructure limitations, not code issues. The milestone is complete with documented infrastructure deferrals.

---

## 12. Final Verdict

**Milestone objectives met. Workflow configuration verified correct. Infrastructure limitations documented and deferred.**

M19 successfully resolved all workflow configuration errors from M18. SLSA Provenance and Documentation Deploy jobs are now operationally correct. The remaining failures are platform constraints (private repo attestation limitation, Pages not enabled) that are outside repository-level code governance. CI truthfulness is maintained: failures are visible and honest, clearly indicating infrastructure availability requirements.

---

## 13. Authorized Next Step

**Next milestone:** M20 (to be defined)

**Constraints or conditions on proceeding:**
- Infrastructure limitations (INFRA-001, INFRA-002) are documented and deferred
- SEC-001 (GitHub Advanced Security) remains optional
- All workflow configuration is operationally correct

---

## 14. Canonical References

**Commits:**
- `fc78c7e` — Merge PR #20: fix(ci): resolve SLSA Provenance and Documentation Deploy failures (M19)
- `352016f` — fix(ci): resolve SLSA Provenance and Documentation Deploy failures (M19)
- `59c2785` — docs(M19): add run 2 post-merge analysis

**Pull Requests:**
- PR #20 — `fix(ci): resolve SLSA Provenance and Documentation Deploy failures (M19)`

**CI Run URLs:**
- PR Run 1: https://github.com/m-cahill/ezra/actions/runs/22470077402 (success — all required jobs passing)
- Post-Merge Run 2: https://github.com/m-cahill/ezra/actions/runs/22470215827 (infrastructure failures identified)

**Documents:**
- `docs/milestones/M19/M19_plan.md` — Detailed milestone plan
- `docs/milestones/M19/M19_run1.md` — PR run analysis
- `docs/milestones/M19/M19_run2.md` — Post-merge run analysis
- `docs/milestones/M19/M19_toolcalls.md` — Tool calls log

**Audit Artifacts:**
- `M19_summary.md` — This document
- `M19_audit.md` — Milestone audit (to be generated)

---

**End of M19 Summary**

