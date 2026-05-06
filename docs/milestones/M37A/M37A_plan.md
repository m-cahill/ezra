# M37A — Required Gate Recovery for Public Release (Plan)

**Status:** Planning (implementation explicitly out of scope for this milestone).

**Context:** M36 merged to `main` (PR #37). Default-branch CI remains **red** on supply-chain and infrastructure-class failures documented in `docs/milestones/M37A/M37A_run1.md` (run `25466391573`). This milestone **plans** behavior-preserving recovery; it does **not** change code, workflows, dependencies, or repository settings.

---

## 1. Intent / Target

- Restore **truthful, explainable default-branch CI** so a public release can trust `main` without conflating **secret-boundary cleanup (M37)** with **gate recovery**.
- Produce a **recovery matrix** classifying each failure: release blocker vs settings limitation vs defer-with-documentation.
- Recommend the **next implementation milestone** (single focused follow-up, e.g. lockfile/supply-chain + workflow gating adjustments), without executing it here.

---

## 2. Scope Boundaries

**In scope:**

- Analysis of four mandated gate classes: **Security / pip-audit**, **Distribution Verification (HTTP 401)**, **Dependency Review**, **SLSA Provenance**.
- Supplemental observation: **Documentation Deploy / GitHub Pages** (failed on the same `main` push run).
- Documentation deliverables: this plan, `M37A_run1.md`, `M37A_toolcalls.md`, ledger updates to `REFACTOR.md` and `docs/ezra.md`.

**Out of scope (hard):**

- Any edits under `src/ezra/**`
- Any edits under `docs/specs/epb_v1/**`
- Any `requirements.txt` or `pyproject.toml` changes
- Any `.github/workflows/**` changes
- Any `.gitignore` or `docs/enhancements/` secret cleanup (M37)
- Weakening, silencing, or `continue-on-error` escalation for **required** security gates
- Changing branch protection or GitHub repo settings via automation

---

## 3. Detected Surfaces & Constraints

| Surface | Observation |
| --- | --- |
| **Repository** | Private, **user-owned** (`owner.type: User`). Affects GitHub **artifact attestations** API (see run log). |
| **GitHub Pages** | `has_pages: false` on repo; Documentation Deploy fails with 404 until Pages is enabled and configured. |
| **Branch protection** | REST `GET .../branches/main/protection` → **404** / not protected. Failing jobs still signal **release risk** even when merge is allowed. |
| **CI workflow** | `ci.yml` runs Distribution Verification on PR, `main` push, and `workflow_dispatch`; job uses `GITHUB_TOKEN` with `contents: read` + `actions: read`. |
| **Release workflow** | Tag-only (`v*`); produces `ezra-distribution`, `ezra-sbom`, `ezra-provenance` artifacts consumed by `scripts/verify_distribution.py`. |
| **Dependency Review job** | Runs only when `github.event_name == 'pull_request'`; **skipped** on `main` push (so not a contributor to run `25466391573` failure, but still relevant on PRs). |
| **Lockfile** | `requirements.txt` pins vulnerable transitive and direct packages (see `M37A_run1.md`). |

---

## 4. Invariants

| Invariant | Verification |
| --- | --- |
| No runtime behavior change | No `src/ezra/**` edits in M37A |
| EPB v1.0.0 schema unchanged | No `docs/specs/epb_v1/**` edits |
| No dependency changes | No `requirements.txt` / `pyproject.toml` edits |
| No workflow changes | No `.github/workflows/**` edits |
| No secret cleanup | No `.gitignore` / enhancements removals |
| CI truthfulness preserved | M37A does not silence checks |
| M37 deferred | Only references; no M37 execution |

---

## 5. Verification Plan

- **Planning artifacts:** `M37A_plan.md`, `M37A_run1.md`, `M37A_toolcalls.md` present and consistent.
- **Evidence:** Post-merge CI run JSON + failed log extracts + local `pip-audit` captured in `M37A_run1.md`.
- **Repo API:** Branch protection + repo facts recorded without committing raw secrets (no full `gh api` dump).

---

## 6. Investigation Steps (completed in planning)

1. ✅ `git status --short`, `git rev-parse HEAD`
2. ✅ `gh run view 25466391573 --json ...` and `--log-failed`
3. ✅ `gh run view 25466391573 --json jobs` (job-level conclusions)
4. ✅ `gh pr view 37 --json ...`
5. ✅ `gh api .../branches/main/protection` (404 documented)
6. ✅ `gh api repos/m-cahill/ezra` — summarized (private, user-owned, `has_pages`)
7. ✅ `pip-audit -r requirements.txt` and JSON (not committed)
8. ✅ Read `ci.yml`, `release.yml`, `scripts/verify_distribution.py`, `tests/test_distribution_verification.py`, `docs/release/DISTRIBUTION_VERIFICATION.md`

**Recommended follow-up investigations (implementation milestone):**

- Confirm GitHub settings: **Actions** default permissions, **fork PR** access, and whether **artifact retention** / cross-workflow access policies differ for private repos.
- If 401 persists with documented scopes, trial **fine-scoped PAT** or **GitHub App** token (maintainer decision) **without** reducing verification rigor.
- Map each vulnerable package to a **single** `pip-compile` bump cadence (possibly one implementation PR).

---

## 7. Proposed Recovery Tracks

### Track 1 — Security Check / `pip-audit`

**Goal:** Plan smallest safe lockfile refresh so `pip-audit --desc` exits 0 on CI.

**Findings:** 11 known issues in 6 packages (see `M37A_run1.md`). Fixing requires **at minimum** addressing `cryptography` (max fix **46.0.7**), `lxml` **6.1.0**, `pillow` **12.2.0**, `pygments` **2.20.0**, `pytest` **9.0.3**, `requests` **2.33.0** (per advisory fix_versions / GHSA).

**Direct vs transitive:** `cryptography`, `pillow`, `pytest` are **direct** in `pyproject.toml`; others largely **transitive** from dev/SBOM stack.

**Implementation approach (future):** edit `pyproject.toml` constraints → `pip-compile` → verify tests / parity policy. **Do not** add ignore lists or disable `pip-audit`.

**Deferral only if:** a fix is impossible without violating another invariant (document with compensating control, e.g. vendor patch) — **not** the case for current advisories.

### Track 2 — Distribution Verification HTTP 401

**Goal:** Determine why artifact ZIP download returns **401** and whether the job is correctly scoped to PR/`main`/release.

**Findings:**

- Failure occurs in `scripts/verify_distribution.py` → `_download_artifact_zip` → `GET .../actions/artifacts/{id}/zip`.
- Job runs on **every** CI trigger including `main` push and PR, with `--tag latest` resolving the latest **Release** workflow run.
- **Design tension:** verifying **release artifacts** on every PR/`main` push implies those artifacts exist and the token can read them from **another** workflow run.

**Classification:** Likely **configuration/token/API entitlement** issue for **private** repo or default **GITHUB_TOKEN** permissions model — **not** a logic error in hash verification itself.

**Truthful design options (implementation):**

1. **Fix token/permissions** so `GITHUB_TOKEN` (or replacement secret) can download artifacts from Release workflow runs while preserving least privilege.
2. **Scope the job:** e.g. run full artifact verification on **tag push / release completion** only; on PR/`main` run a **narrow** check (local `python -m build` + hash self-check without cross-workflow download) if artifact download is impossible on PRs.
3. **Split jobs:** `distribution-verification-pr` (static checks) vs `distribution-verification-release` (downloads).

**Doc inconsistency:** `docs/release/DISTRIBUTION_VERIFICATION.md` states CI “does not block merges”; the job still fails the workflow run when red. Implementation should align **documentation**, **branch protection**, and **job requirements**.

### Track 3 — Dependency Review

**Goal:** Clarify whether `dependency-review-action` can succeed for this repo/account.

**Findings:**

- Workflow marks job `continue-on-error: true` and adds a note about **GitHub Advanced Security**.
- On **`main` push**, the job is **skipped** entirely (`if: pull_request`).
- On **PRs**, expect failures when **dependency graph / GHAS** features are unavailable for the account/repo tier.

**Classification:** **Infrastructure / licensing** — not fixable by Python code changes alone.

**Recommendations (implementation / governance):**

- Maintain **warn-first** posture OR document **unavailable on private free-tier** explicitly in `REFACTOR.md` / release readiness matrix.
- **Blocking** Dependency Review only after GHAS (or equivalent) is enabled and proven stable.

### Track 4 — SLSA Provenance / attestation

**Goal:** Classify CI provenance failure vs private-repo limitation.

**Findings (run `25466391573`):**

- **Job:** SLSA Provenance  
- **Step:** Generate provenance attestation (`actions/attest-build-provenance`)  
- **Error:** `Failed to persist attestation: Feature not available for user-owned private repositories. ... make this repository public`

**Classification:** **Expected limitation** for current repo visibility/ownership — **not** a misconfigured step in isolation.

**Truthful paths:**

- **Defer** public attestation until repo is public (document limitation in release docs).
- **Implementation** alternatives: non-GitHub attestation, or remove/split job for private phase **only** with explicit documentation that SLSA is **not claimed** for private builds (requires careful wording — do not claim green SLSA when unavailable).

### Track 5 — Documentation Deploy (supplemental)

**Failure:** Deploy to GitHub Pages — **404**, Pages not enabled.

**Classification:** **Settings** — enable GitHub Pages or disable/deploy conditionally in a **future** workflow change (out of scope for M37A).

---

## 8. Risk & Rollback Plan

| Risk | Mitigation |
| --- | --- |
| Lockfile bumps change behavior | Run full test matrix + parity policy; pin minimal versions |
| Token elevation expands blast radius | Prefer documented `GITHUB_TOKEN` scopes first; PAT last resort with minimal ACL |
| Mis-stating SLSA posture | Document “not available on private user repo” explicitly |
| Splitting verification weakens guarantees | Compensate with **release-only** full verification gate |

**Rollback:** Implementation PRs should be small and revertible; no M37A rollback needed (docs-only milestone).

---

## 9. Deliverables

| Deliverable | Path |
| --- | --- |
| Plan | `docs/milestones/M37A/M37A_plan.md` |
| Evidence | `docs/milestones/M37A/M37A_run1.md` |
| Tool log | `docs/milestones/M37A/M37A_toolcalls.md` |
| Ledger | `REFACTOR.md` (M37A section) |
| Milestone index | `docs/ezra.md` (M37A row) |

---

## 10. Exit Criteria

- [x] Recovery matrix complete with classifications and recommended next milestone column.
- [x] `M37A_run1.md` contains command outputs / summarized API facts.
- [x] No forbidden file classes modified in M37A commits.
- [ ] **Future:** Dedicated **implementation** milestone executes fixes and re-runs CI.

---

## 11. Explicit Non-Goals

- M37 secret-path cleanup.
- Merging M37A PR without maintainer review.
- Claiming SLSA/provenance is satisfied when GitHub refuses attestation.
- Replacing Dependency Review with a no-op.

---

## Recovery matrix

| Gate | Current Failure | Classification | Likely Fix | Risk | Recommended Milestone |
| --- | --- | --- | --- | --- | --- |
| Security / pip-audit | 11 vulns in 6 packages; step **Run pip-audit** fails | **Real supply-chain debt** in lockfile | `pyproject.toml` constraint bumps + `pip-compile` regenerate lockfile | Medium — test/optional-ML paths | **Post-M37A implementation** (supply-chain; call **M37B** or next numbered milestone) |
| Distribution Verification | HTTP **401** on artifact ZIP download | **Token / API access** + possible **job scope** mismatch | Fix `GITHUB_TOKEN` or repo Actions permissions; and/or restrict full verification to **tag/release**; optionally split PR-safe vs release jobs | Medium — wrong split could miss regressions | **Same implementation milestone as workflow gating** (after M37A approval) |
| Dependency Review | GHAS / graph unavailable; PR-only; workflow warn-first | **Infra / product tier** | Enable GHAS OR document **unavailable** + keep warn-first | Low — policy clarity | **Settings + documentation** (no code) or defer until org upgrades |
| SLSA Provenance | Attestation persist blocked for **user-owned private** repo | **Platform limitation** | Document; make job conditional on **public** or switch attestation strategy | Low for private preview; **revisit** at public release | **Documentation + conditional workflow** (implementation after plan approval) |
| **Documentation Deploy** (supplemental) | Pages **404** / not enabled | **Repo settings** | Enable GitHub Pages or skip deploy on private | Low | **Settings** or small workflow/doc follow-up |

---

## Recommended next implementation milestone (after M37A review)

Single suggested follow-up (name TBD by maintainer, e.g. **M37B**):

1. **Regenerate lockfile** to clear `pip-audit` (minimal version bumps).
2. **Distribution Verification:** resolve **401** (permissions/PAT/repository settings) and **align job triggers** with when release artifacts exist; update `docs/release/DISTRIBUTION_VERIFICATION.md` to match required vs optional semantics.
3. **SLSA / Pages / Dependency Review:** document limitations or gate jobs on repo visibility/settings **without** falsely claiming green provenance.

**M37 (secret cleanup)** can proceed **in parallel** from a scope perspective, but **public-release “CI green”** should not be treated as achieved until the **implementation** above (or explicit documented deferral) is done.
