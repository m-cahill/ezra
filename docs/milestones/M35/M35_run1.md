# M35 Run 1 — CI Workflow Analysis

**Milestone:** M35 — EZRA Operating Manual (AI-Agent Ready, Verified)  
**Workflow:** CI  
**Run ID:** 23362721199  
**Trigger:** pull_request (PR #36)  
**Branch:** m35-operating-manual  
**Commit:** 35b19e9 (M35: EZRA Operating Manual (AI-Agent Ready, Verified))

---

## 1. Workflow Identity

| Field | Value |
|-------|--------|
| Workflow name | CI |
| Run ID | 23362721199 |
| Trigger | pull_request |
| Branch | m35-operating-manual |
| PR | #36 |
| Run URL | https://github.com/m-cahill/ezra/actions/runs/23362721199 |
| Head SHA | 35b19e903bf11e21a360c88d47185acec46e12fe |
| Overall conclusion | **failure** (workflow failed; see below for merge-blocking vs. non-blocking) |

---

## 2. Change Context

| Field | Value |
|-------|--------|
| Milestone | M35 — EZRA Operating Manual |
| Declared intent | Add `docs/ezra_operating_manual_v1.md`, `docs/certification/README.md`, M35 milestone artifacts, update `docs/ezra.md` + `README.md`; no runtime or EPB changes |
| Refactor target surface | Documentation and governance linking only |
| Posture | Behavior-preserving (documentation only) |
| Run type | Governance / documentation |

---

## 3. Baseline Reference

- **PR:** #36 — M35: EZRA Operating Manual (AI-Agent Ready, Verified)
- **M29/M31 hermetic baseline hash (unchanged expectation):** `c186777c33b7b7b9d11540bda7398efd0dfb085143506513a4ce87836c6ac7c2`
- **Declared invariants:** No EPB/schema/canonicalization/hashing/plugin contract changes from M35 doc work.

---

## Step 1 — Workflow Inventory

| Job / Check | Required? | Purpose | Pass/Fail | Notes |
|-------------|------------|---------|-----------|-------|
| Lint | Yes | Ruff + Pydocstyle | **Fail** | E501 line length in `scripts/verify_distribution.py` (lines 147, 188) — **not caused by M35 doc edits**; see Step 3 |
| Type Check | Yes | Mypy | Pass | |
| EPB Tools Minimal Environment | Yes | Minimal env + `pip install -e .` | Pass | |
| Smoke Tests | Yes | Fast contract subset | Pass | |
| Test | Yes | Pytest, coverage ≥85%, zone/EPB steps | Pass | |
| Security Check | Yes | Bandit, pip-audit, gitleaks | Pass | |
| SBOM Generation | Yes | CycloneDX | Pass | |
| Complexity Check | Yes | Radon | Pass | |
| Determinism Check | Yes | Triple-run byte-identical bundles | Pass | |
| Hermetic Hash (Py 3.10 / 3.11 / 3.12) | Yes | Per-version canonical bundle hash | Pass | |
| Hermetic Reproducibility | Yes | Cross-matrix hash comparison | Pass | |
| Documentation Build | Yes | Sphinx | Pass | |
| Dependency Review | continue-on-error | GH dependency graph / GHAS | **Fail** | SEC-001 infra: "Dependency review is not supported on this repository" — **non-blocking** (expected) |
| OpenSSF Scorecard | continue-on-error | Informational | Pass | |
| SLSA Provenance | Conditional | push main/tags | Skipped | PR trigger |
| Documentation Deploy | Conditional | push main | Skipped | PR trigger |
| Distribution Verification | Yes* | `verify_distribution.py --tag latest` | **Fail** | HTTP 401 on artifact download via `GITHUB_TOKEN` — **infrastructure/permissions**, not M35 docs; see Step 4 |

\*Confirm in `ci.yml` whether `distribution-verification` is merge-blocking for PRs; job has no `continue-on-error` in workflow file — failure turns workflow red even when other required jobs pass.

---

## Step 2 — Refactor Signal Integrity (M35 Scope)

### A) Tests

- M35 changes are documentation-only. Test job **passed** — no regression signal from M35 files.

### B) Coverage

- Test job passed with existing coverage gate — no M35 impact.

### C) Static / Policy Gates

- **Lint failed** on `scripts/verify_distribution.py` (E501). M35 PR did not modify that file; failure is **orthogonal** to operating manual content but **blocks merge** until Ruff is clean.

### D) EPB / Determinism / Hermetic

- Determinism, hermetic matrix, and hermetic reproducibility jobs **passed** — consistent with "no EPB/runtime change" posture for M35.

### E) Documentation

- Documentation Build **passed** — new markdown and Sphinx build are compatible with CI.

---

## Step 3 — Lint Failure (Merge-Blocking)

**Tool:** Ruff (`ruff check --no-fix .`)

**Errors:**

| Code | File | Line | Issue |
|------|------|------|-------|
| E501 | `scripts/verify_distribution.py` | 147 | Line too long (105 > 100) |
| E501 | `scripts/verify_distribution.py` | 188 | Line too long (118 > 100) |

**Root cause:** Line-length violations in distribution verification script. Not introduced by M35 documentation commits.

**Remediation:** Wrap or split the long condition and comprehension so each line ≤ 100 characters; re-run Ruff locally and push a follow-up commit on `m35-operating-manual`.

---

## Step 4 — Distribution Verification Failure

**Command:** `python scripts/verify_distribution.py --tag latest`

**Outcome:** `urllib.error.HTTPError: HTTP Error 401: Server failed to authenticate the request`

**Interpretation:** The default `GITHUB_TOKEN` in PR workflows may lack permission to download Actions artifacts from the Release workflow (or token scope / repository settings). This is an **integration/permissions** issue, not a logic error in M35 docs.

**Relation to M35:** None. Same class of issue as documented for M34 (expected failures when provenance/artifacts unavailable).

**Options (governance, not M35 scope):** Grant `actions: read` + artifact access where supported, use `continue-on-error` for this job on `pull_request`, or document as known infra limitation.

---

## Step 5 — Dependency Review Failure

**Message:** Dependency review is not supported on this repository (enable Dependency graph + GitHub Advanced Security).

**Classification:** SEC-001 / infra — **non-blocking** (`continue-on-error: true` in workflow).

---

## Step 6 — Verdict (Run 1)

| Question | Answer |
|----------|--------|
| Did M35 doc changes break tests, typecheck, EPB, or determinism? | **No** — those jobs passed. |
| Is the workflow green? | **No** — Lint failed (E501); Distribution Verification failed (401). |
| Safe to merge on doc merit alone? | **No** — merge requires addressing **required** failing checks per branch protection. |
| Recommended next step | Fix Ruff E501 on `verify_distribution.py` (quick mechanical fix); re-run CI. Address Distribution Verification policy separately if it remains required on PRs. |

---

## Step 7 — Post–Run 1 Remediation (Lint)

**E501** on `scripts/verify_distribution.py` (lines 147 and 188) was fixed by wrapping the long `if` condition and the dict comprehension across multiple lines. **Ruff** passes locally on that file after the change.

This remediation is **mechanical** (line length only); it does not change script behavior. A follow-up CI run (Run 2) should be used to confirm Lint is green on the PR.

**Distribution Verification** (401) remains a separate permissions/infra topic for Run 2 analysis.

---

## Step 8 — Canonical References

- **PR:** https://github.com/m-cahill/ezra/pull/36  
- **Run ID:** 23362721199  
- **URL:** https://github.com/m-cahill/ezra/actions/runs/23362721199  
- **Plan:** `docs/milestones/M35/M35_plan.md`  
- **Summary:** `docs/milestones/M35/M35_summary.md`  
- **Audit:** `docs/milestones/M35/M35_audit.md`
