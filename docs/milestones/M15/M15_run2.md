# M15 CI Run Analysis — Run 2 (After SBOM Command Fix)

**Workflow:** CI  
**Run ID:** 22465701522  
**Trigger:** Pull Request #16  
**Branch:** `m15-ci-evidence-hardening`  
**Commit:** `da3619d` (merge commit after SBOM command syntax fix)  
**URL:** https://github.com/m-cahill/ezra/actions/runs/22465701522  
**Conclusion:** ⚠️ **PARTIAL SUCCESS** (6/7 jobs passed, SBOM Generation failed)

---

## 1. Workflow Identity

- **Workflow Name:** CI
- **Run ID:** 22465701522
- **Trigger:** Pull Request #16 (`m15-ci-evidence-hardening`)
- **Branch:** `m15-ci-evidence-hardening`
- **Commit SHA:** `da3619d` (merge commit after SBOM command syntax fix)
- **PR Number:** #16
- **Run History:** Third run — first run failed on dependency installation (fixed), second run failed on SBOM command syntax (fixed), this run still has SBOM issue

---

## 2. Change Context

- **Milestone:** M15 — CI Evidence & Deterministic Quality Envelope Hardening
- **Declared Intent:** Governance and signal-strengthening milestone. Add structured CI job summaries, upload machine-readable artifacts (coverage, radon, security JSON, etc.), introduce deterministic quality dashboards, formalize quality envelope contracts. **No runtime code changes.**
- **Refactor Target Surface:**
  - Modified: `.github/workflows/ci.yml` (added 3 new jobs: security, complexity, sbom; enhanced test job summary; fixed SBOM command to use `environment` subcommand)
  - Modified: `pyproject.toml` (added dev dependencies: radon, bandit, pip-audit, cyclonedx-py>=1.0.0)
  - Modified: `.gitignore` (added CI artifact patterns)
  - New: `docs/qa.md` (comprehensive QA documentation with compliance mapping)
- **Posture:** **Governance-only (no runtime changes)** — CI workflow updates only, artifact uploads, documentation. No runtime code changes, no new domain features, no plugin additions, no architectural layer movement.
- **Run Type:** Corrective (after fixing SBOM command to use `environment` subcommand)

---

## 3. Baseline Reference

- **Last Known Trusted Green:** `v0.0.15-m14` (tag)
- **Declared Invariants:**
  - All 205 tests pass
  - 4 skipped tests remain skipped
  - Determinism script passes
  - No new architecture violations
  - No behavior drift
  - Tag v0.0.15-m14 remains valid
  - No public API changes
  - Coverage must not drop below baseline (≥85%)
  - **NEW:** Quality gates produce structured, auditable, machine-readable evidence

---

## 4. Workflow Inventory

| Job / Check | Required? | Purpose | Pass/Fail | Notes |
|-------------|-----------|---------|-----------|-------|
| Lint | ✅ Yes | Ruff lint + format check | ✅ **PASS** | All checks passed |
| Type Check | ✅ Yes | Mypy type checking | ✅ **PASS** | All checks passed |
| Test | ✅ Yes | Pytest with coverage | ✅ **PASS** | 205 passed, 4 skipped, 95.69% coverage (above 85% threshold) |
| Security Check | ✅ Yes (NEW) | Bandit, pip-audit, gitleaks | ✅ **PASS** | 0 HIGH issues (bandit), 0 vulnerabilities (pip-audit), 0 leaks (gitleaks) |
| Complexity Check | ✅ Yes (NEW) | Radon complexity analysis | ✅ **PASS** | All functions grade C or better, no D/E grades found |
| SBOM Generation | ✅ Yes (NEW) | CycloneDX SBOM generation | ❌ **FAIL** | Command syntax error: `-e` flag not recognized by `cyclonedx-py environment` |
| Determinism Check | ✅ Yes | Multi-run bundle determinism verification | ✅ **PASS** | All determinism checks passed |

**All checks are merge-blocking.** No checks use `continue-on-error` (except summary steps which use `if: always()`).

**New Checks Added:**
- **Security Check** — Bandit (fail on HIGH), pip-audit (strict), gitleaks (detect mode)
- **Complexity Check** — Radon (fail on grade > C)
- **SBOM Generation** — CycloneDX SBOM generation (currently failing due to invalid `-e` flag)

**Critical Observation:** 6 out of 7 jobs passed successfully. SBOM Generation failed due to invalid flag — `cyclonedx-py environment` does not recognize the `-e` flag. The command `cyclonedx-py environment -o sbom.cdx.json -e` fails with "unrecognized arguments: -e".

---

## 5. Refactor Signal Integrity

### A) Tests

- **Tiers Ran:** Unit tests (205 passed, 4 skipped)
- **Coverage of Refactor Target:** N/A — no runtime code changes in this milestone
- **Failures:** None
- **Golden/Snapshot Tests:** All determinism tests passed
- **Missing Tests:** N/A — no new runtime code to test

**Test Results:**
- ✅ 205 tests passed
- ⏭️ 4 tests skipped (unchanged from baseline)
- ✅ Coverage: 95.69% (above 85% threshold)
- ✅ All determinism checks passed

### B) Coverage

- **Enforcement:** Line + branch coverage, ≥85% threshold (unchanged)
- **Scoped Correctly:** Yes — coverage measures `src/` directory only
- **Exclusions:** None introduced/expanded
- **Coverage Change:** 95.69% (maintained above 85% threshold)

**Coverage Breakdown:**
- Total: 672 statements, 19 missed, 210 branches, 19 partial
- Coverage: 95.69% (exceeds 85% threshold)
- Lowest coverage module: `src/ezra/epb/schema_validator.py` (79.66%) — acceptable

### C) Static / Policy Gates

- **Linting:** ✅ Passed — Ruff found no issues
- **Type Checking:** ✅ Passed — Mypy found no issues
- **Formatting:** ✅ Passed — Ruff format check passed

### D) Security / Supply Chain Signals

- **Bandit:** ✅ Passed — 0 HIGH severity issues (1 LOW issue found, not blocking)
- **pip-audit:** ✅ Passed — No known vulnerabilities found
- **Gitleaks:** ✅ Passed — No secrets detected
- **SBOM:** ❌ Failed — Invalid `-e` flag

**Security Summary:**
- Bandit: 0 HIGH issues, 1 LOW issue (non-blocking)
- pip-audit: Clean (no vulnerabilities)
- Gitleaks: Clean (no secrets detected)

### E) Performance / Benchmarks

- **N/A** — No performance benchmarks in this milestone

---

## 6. Delta Analysis (Change Impact vs Baseline)

### Change Inventory

**Files Modified:**
- `.github/workflows/ci.yml` — Added 3 new jobs (security, complexity, sbom), enhanced test job summary, fixed SBOM command to use `environment` subcommand
- `pyproject.toml` — Added dev dependencies: radon>=6.0.0, bandit>=1.7.0, pip-audit>=2.6.0, cyclonedx-py>=1.0.0
- `.gitignore` — Added CI artifact patterns (sbom.cdx.json, bandit.json, pip_audit.json, radon.json, radon.txt)
- `docs/qa.md` — New comprehensive QA documentation

**Public Surfaces Touched:**
- None — no runtime code changes, no API changes, no schema changes

### Expected vs Observed Deltas

**Expected:**
- New CI jobs added (security, complexity, sbom)
- Enhanced test job summary with structured Quality Envelope
- Artifact uploads for all quality evidence
- All existing checks continue to pass

**Observed:**
- ✅ 6 out of 7 jobs passed successfully
- ✅ All existing checks continue to pass
- ✅ New quality gates execute and produce artifacts (security, complexity)
- ❌ SBOM generation failed due to invalid `-e` flag
- ✅ Coverage maintained at 95.69% (above 85% threshold)
- ✅ Determinism gate passed

### Refactor-Specific Drift Detection

**Signal Drift:**
- None — all quality gates execute correctly (except SBOM flag issue)

**Coupling Revealed:**
- None — new jobs are independent and do not affect existing checks

**Hidden Dependencies:**
- None — all failures are explicit and traceable

---

## 7. Failure Analysis

### Failure Classification

**Type:** CI misconfiguration  
**Root Cause:** Invalid flag `-e` for `cyclonedx-py environment` command  
**Details:**
- Command used: `cyclonedx-py environment -o sbom.cdx.json -e`
- Error: `cyclonedx-py: error: unrecognized arguments: -e`
- Issue: The `-e` flag is not a valid argument for the `environment` subcommand

**Is this in-scope for the milestone?** ✅ Yes — SBOM generation is part of M15 implementation  
**Is it blocking?** ✅ Yes — blocks SBOM artifact generation  
**Is it deferrable?** ❌ No — must be fixed to complete milestone

### Fix Required

**Action:** Remove the invalid `-e` flag from SBOM generation command in `.github/workflows/ci.yml`:
```yaml
# Current (incorrect):
cyclonedx-py environment -o sbom.cdx.json -e

# Should be:
cyclonedx-py environment -o sbom.cdx.json
```

**Status:** ⏳ **Pending** — Fix not yet applied

**Note:** The `-e` flag was likely intended to indicate "environment" mode, but the `environment` subcommand already implies this. The `-o` flag for output should be sufficient.

---

## 8. Invariants & Guardrails Check

### Invariant Verification Status

| Invariant | Status | Evidence |
|-----------|--------|----------|
| Required checks remain enforced | ✅ Preserved | No checks weakened, no `continue-on-error` added to blocking checks |
| Refactor did not expand scope into feature work | ✅ Preserved | Only CI workflow and documentation changes |
| Public surfaces remained compatible | ✅ Preserved | No runtime code changes |
| Schema/contract outputs remain valid | ✅ Preserved | No schema changes |
| Determinism/golden outputs preserved | ✅ Preserved | All determinism checks passed |
| No "green but misleading" path | ✅ Preserved | Failure is explicit and traceable |
| Coverage threshold maintained | ✅ Preserved | 95.69% (above 85% threshold) |

**Critical Observation:** All invariants are preserved. The SBOM failure is a configuration error (invalid flag), not a refactor drift or invariant violation. The fix is straightforward.

---

## 9. Verdict

**Verdict:**  
CI run shows 6 out of 7 jobs passed successfully. All existing quality gates continue to pass, new security and complexity gates execute correctly and produce expected artifacts, coverage is maintained at 95.69% (above 85% threshold), and determinism checks pass. The only failure is SBOM generation due to invalid `-e` flag — `cyclonedx-py environment` does not recognize this flag. This is a configuration error, not a refactor issue. All invariants are preserved. No runtime code changes were made. The failure is explicit, traceable, and fixable. Once the invalid `-e` flag is removed from the SBOM command, all jobs should pass.

**Recommended Outcome:**  
🔁 **Re-run required** — Fix SBOM command by removing invalid `-e` flag, then verify all jobs pass.

---

## 10. Next Actions

| ID | Task | Owner | Scope | Milestone | Guardrail |
|----|------|-------|-------|-----------|-----------|
| 1 | Fix SBOM command: remove invalid `-e` flag (use `cyclonedx-py environment -o sbom.cdx.json`) | Cursor | `.github/workflows/ci.yml` | M15 | Re-run CI after fix |
| 2 | Verify SBOM artifact is generated and uploaded correctly | Cursor | CI artifacts | M15 | Download and inspect SBOM artifact |
| 3 | Verify all quality gates pass after SBOM fix | Cursor | CI workflow | M15 | Check all job outputs |

**All actions are in-scope for M15.** No new milestone required.

---

## 11. Minimal Fix Set

**Fix Required:**
- ⏳ Update `.github/workflows/ci.yml`: Change `cyclonedx-py environment -o sbom.cdx.json -e` to `cyclonedx-py environment -o sbom.cdx.json`

**Verification Required:**
- Re-run CI to confirm all jobs pass with corrected SBOM command
- Verify SBOM artifact is generated and uploaded correctly
- Verify all quality gates execute and produce expected artifacts

---

## 12. CI Root Cause Summary

**Third Run Status:**
- **Issue:** SBOM Generation job failed
- **Root Cause:** Invalid `-e` flag — `cyclonedx-py environment` does not recognize this flag
- **Resolution:** Remove `-e` flag from command (use `cyclonedx-py environment -o sbom.cdx.json`)
- **Status:** ⏳ **Pending** — Fix not yet applied

**Other Jobs:**
- ✅ Lint: Passed
- ✅ Type Check: Passed
- ✅ Test: Passed (205 passed, 4 skipped, 95.69% coverage)
- ✅ Security Check: Passed (0 HIGH issues, 0 vulnerabilities, 0 leaks)
- ✅ Complexity Check: Passed (all functions grade C or better)
- ✅ Determinism Check: Passed

**Next Run Expected:**
- All 7 jobs should pass successfully
- SBOM artifact should be generated and uploaded
- All quality gates should produce expected artifacts

---

**End of Analysis**

