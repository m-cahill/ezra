# M19 CI Run Analysis — Run 2 (Post-Merge)

**Workflow:** CI  
**Run ID:** 22470215827  
**Trigger:** Push to `main` (merge of PR #20)  
**Branch:** `main`  
**Commit:** `fc78c7e`  
**URL:** https://github.com/m-cahill/ezra/actions/runs/22470215827  
**Conclusion:** ❌ **FAILURE** (10/12 jobs passed, 2 failures)

---

## 1. Workflow Identity

- **Workflow Name:** CI
- **Run ID:** 22470215827
- **Trigger:** Push to `main` (merge commit from PR #20)
- **Branch:** `main`
- **Commit SHA:** `fc78c7e` (Merge PR #20: fix(ci): resolve SLSA Provenance and Documentation Deploy failures)
- **Run History:** Post-merge run — verifying CI-001 and CI-002 fixes on main

---

## 2. Change Context

- **Milestone:** M19 — Post-Merge CI Integrity & Release Attestation Closure
- **Declared Intent:** Verify SLSA Provenance and Documentation Deploy pass on main push
- **Refactor Target Surface:** `.github/workflows/ci.yml` only
- **Posture:** CI-only, no runtime changes

---

## 3. Baseline Reference

- **Last Known Trusted Green (PR):** Run 22470077402 (PR #20, all required jobs passing)
- **Previous Post-Merge Failure:** Run 22469515181 (M18 merge, CI-001/CI-002 failed due to config)

---

## 4. Workflow Inventory

| Job / Check | Required? | Purpose | Pass/Fail | Notes |
|-------------|-----------|---------|-----------|-------|
| Lint | Yes | Ruff lint + format + pydocstyle | ✅ **PASS** | All checks passed |
| Type Check | Yes | Mypy type checking | ✅ **PASS** | All checks passed |
| Test | Yes | Pytest with coverage | ✅ **PASS** | 214 passed, 4 skipped |
| Security Check | Yes | Bandit, pip-audit, gitleaks | ✅ **PASS** | All security checks passed |
| Complexity Check | Yes | Radon complexity analysis | ✅ **PASS** | All functions grade C or better |
| SBOM Generation | Yes | CycloneDX SBOM generation | ✅ **PASS** | SBOM generated |
| Determinism Check | Yes | Multi-run bundle determinism | ✅ **PASS** | All determinism checks passed |
| OpenSSF Scorecard | Informational | Security posture assessment | ✅ **PASS** | Warn-first, SARIF uploaded |
| Documentation Build | Yes | Sphinx documentation build | ✅ **PASS** | Docs built, Pages artifact uploaded |
| Dependency Review | Conditional | Dependency change review | ⏭️ **SKIPPED** | Expected on push (PR-only job) |
| SLSA Provenance | Yes (main) | Build attestation | ❌ **FAIL** | **Ran** (not skipped). See analysis below. |
| Documentation Deploy | Yes (main) | GitHub Pages deployment | ❌ **FAIL** | **Ran** (not skipped). See analysis below. |

**Key observation:** Both target jobs now **run** on main push (not skipped). The configuration fixes are working. Failures are due to repository-level settings, not workflow configuration.

---

## 5. Failure Analysis

### CI-001: SLSA Provenance — INFRASTRUCTURE LIMITATION

**Step:** Generate provenance attestation  
**Error:**
```
Error: Failed to persist attestation: Feature not available for user-owned
private repositories. To enable this feature, please make this repository
public. - https://docs.github.com/rest/repos/attestations#create-an-attestation
```

**Root Cause:** GitHub attestation API does not support **user-owned private repositories**. Attestations are only available for:
- Public repositories
- Organization-owned repositories with appropriate plan

**Configuration Status:** ✅ **CORRECT**
- `subject-path: dist/` is accepted (no "unexpected input" warning)
- Provenance predicate is correctly generated with proper commit SHA
- Permissions are correct (`id-token: write`, `contents: write`, `attestations: write`)
- Build step produces artifacts successfully
- The attestation is generated but cannot be persisted

**This is NOT a workflow configuration error.** The workflow is operationally correct. The limitation is at the GitHub platform level for this repository type.

**Resolution options:**
1. Make repository public (enables attestations)
2. Move to an organization (may enable with appropriate plan)
3. Accept as known infrastructure limitation and defer

---

### CI-002: Documentation Deploy — PAGES NOT ENABLED

**Step:** Deploy to GitHub Pages  
**Error:**
```
Error: Failed to create deployment (status: 404) with build version
fc78c7e93c6180084f081db214ea070aaa9118d7.
Ensure GitHub Pages has been enabled:
https://github.com/m-cahill/ezra/settings/pages
```

**Configuration Status:** ✅ **CORRECT**
- `upload-pages-artifact@v3` produced artifact correctly
- `deploy-pages@v4` found the artifact: `Found 3 artifact(s)`
- OIDC token obtained successfully (permissions fix worked)
- Deployment payload correctly constructed with artifact ID and build version
- The only missing piece is Pages must be enabled in repository settings

**This is NOT a workflow configuration error.** The workflow is operationally correct. The failure is expected per locked decisions: "If Pages is not enabled, the job may fail. That failure is acceptable during development."

**Resolution:** Enable GitHub Pages in repository settings (Settings > Pages > Source: GitHub Actions)

---

## 6. Configuration Fix Verification

### CI-001 Fixes Verified

| Fix | Pre-M19 Error | Post-M19 Behavior | Status |
|-----|---------------|-------------------|--------|
| Remove `build-workflow-path` | Warning: unexpected input | No warning | ✅ Fixed |
| Add `subject-path: dist/` | Error: One of subject-path or subject-digest must be provided | subject-path accepted, attestation generated | ✅ Fixed |

The M18 configuration errors are resolved. The remaining failure is an infrastructure limitation.

### CI-002 Fixes Verified

| Fix | Pre-M19 Error | Post-M19 Behavior | Status |
|-----|---------------|-------------------|--------|
| Add `id-token: write` permission | Unable to get ACTIONS_ID_TOKEN_REQUEST_URL | OIDC token obtained successfully | ✅ Fixed |
| Add `pages: write` permission | (blocked by id-token error) | Deployment payload constructed | ✅ Fixed |
| Add `upload-pages-artifact@v3` | (artifact not found) | Found 3 artifact(s) | ✅ Fixed |
| Add `environment: github-pages` | (no environment) | Environment configured | ✅ Fixed |
| Remove redundant rebuild | (wasted CI time) | Single build in docs-build, deploy-only in docs-deploy | ✅ Fixed |

The M18 configuration errors are resolved. The remaining failure is that Pages is not enabled in repository settings.

---

## 7. Invariant Verification

| Invariant | Status | Evidence |
|-----------|--------|----------|
| All 214 tests pass | ✅ PASS | CI test job |
| 4 skipped tests remain skipped | ✅ PASS | CI test job |
| Determinism script passes | ✅ PASS | CI determinism job |
| EPB v1.0.0 schema unchanged | ✅ PASS | No schema changes |
| Hash algorithm unchanged | ✅ PASS | No hash changes |
| Exception hierarchy unchanged | ✅ PASS | No exception changes |
| Coverage >= baseline (>=85%) | ✅ PASS | CI coverage check |
| All existing CI jobs remain green | ✅ PASS | 10/10 pre-existing jobs passed |
| No runtime behavior changes | ✅ PASS | CI-only changes |
| No continue-on-error on provenance/docs-deploy | ✅ PASS | Verified — both fail visibly |

**All invariants preserved. Both jobs fail honestly (no masking).**

---

## 8. Comparison: M18 Post-Merge vs M19 Post-Merge

| Job | M18 Post-Merge Error | M19 Post-Merge Error | Configuration Fixed? |
|-----|---------------------|---------------------|---------------------|
| SLSA Provenance | `Unexpected input 'build-workflow-path'` + `One of subject-path or subject-digest must be provided` | `Feature not available for user-owned private repositories` | ✅ Yes — config correct, infra limitation |
| Documentation Deploy | `Unable to get ACTIONS_ID_TOKEN_REQUEST_URL` + `Ensure GITHUB_TOKEN has permission "id-token: write"` | `Failed to create deployment (status: 404)` + `Ensure GitHub Pages has been enabled` | ✅ Yes — config correct, Pages not enabled |

**Both workflow configuration errors from M18 are resolved.** Remaining failures are repository-level settings/limitations.

---

## 9. Assessment

### What M19 achieved:

1. **CI-001 workflow configuration is now correct.** The SLSA Provenance job properly builds the package, generates the attestation predicate, and attempts to persist it. The failure is a GitHub platform limitation for private user-owned repos.

2. **CI-002 workflow configuration is now correct.** The Documentation Deploy job correctly obtains OIDC tokens, finds the Pages artifact, and constructs the deployment payload. The failure is that Pages is not enabled in repo settings.

3. **Both jobs fail honestly.** No `continue-on-error`, no masking. Green means green. The error messages clearly indicate what repository settings need to change.

4. **All runtime invariants preserved.** 214 tests pass, determinism intact, coverage maintained, no behavioral changes.

### What remains:

- **CI-001:** Repository must be public or organization-owned for attestations to work
- **CI-002:** GitHub Pages must be enabled in repository settings (Settings > Pages > Source: GitHub Actions)
- **SEC-001:** GitHub Advanced Security (pre-existing, deferred)

---

## 10. Recommendation

The workflow configuration is operationally correct. The remaining failures are **repository settings** that must be changed by the repository owner. These are not workflow bugs.

**Options for milestone closure:**
1. Enable Pages + make repo public → both jobs pass → clean close
2. Accept infrastructure limitations as documented known state → close with documented deferrals
3. Make jobs conditional on repo type/settings → rejected by locked decisions (no downgrading)

---

**End of Run 2 Analysis (Post-Merge)**

