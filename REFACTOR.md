# EZRA Refactor Ledger

This document is the authoritative refactor-program ledger for public-release readiness work from M36 onward.

`docs/ezra.md` remains the canonical project governance and architecture ledger. This file records refactor-specific milestone decisions, audit reconciliation outcomes, public-release boundary decisions, and follow-up hooks.

---

## M36 — Audit Reconciliation & Public Release Boundary Inventory

**Status:** Closed — Proceed to M37

**Summary:**

M36 reconciled the M33/Post-M32 full audit (`docs/M33fullaudit.md`, commit `23789314ba5f6a502c650f6a098f12eb4ed0e8b4`, weighted score **4.95**) against the M35/current full audit (external planning artifact at commit `f12fd083b1b0e9f9c518535e0938b65d204b5075`, weighted score **4.40**). The **−0.55** overall delta is assessed as **primarily audit calibration drift and public-release-readiness polish**, not a true project regression: Architecture, Tests & CI, and Security remained **5/5** in both audits; deltas concentrate on Modularity, Code Health, Performance, DX, and Docs where the later audit applied a stricter consumer-facing lens without contradicting M33’s factual claims.

**Secret-boundary inventory** (command `git ls-files .cursorrules docs/enhancements docs/prompts` at M36 closeout): only `docs/enhancements/` files were listed as tracked; `.cursorrules` and `docs/prompts/` had **no** tracked paths at that moment. **Historical note:** `git diff 23789314..HEAD` shows `.cursorrules` and former `docs/prompts/**` paths as removed in that interval—i.e. the repo already moved those out of Git in later work; M36 performed **no** cleanup. M37 remains authorized to add ignore/guardrails for all three user-approved paths.

**Evidence artifacts:** `docs/release/AUDIT_RECONCILIATION_M33_M35.md`, `docs/milestones/M36/M36_plan.md`, `docs/milestones/M36/M36_run1.md`, `docs/milestones/M36/M36_summary.md`, `docs/milestones/M36/M36_audit.md`, `docs/milestones/M36/M36_pr1_ci_triage.md`, `docs/milestones/M36/M36_merge.md`.

**M36 constraints honored:** No changes under `src/ezra/`, no EPB schema/spec edits, no `.github/workflows/**` edits, no dependency or `.gitignore` edits, no secret untracking in M36.

### PR #37 CI triage

PR #37 CI run `25465492721` failed on pre-existing or infrastructure-related checks, not on M36 documentation changes. Type Check passed on Linux CI, so the local Windows `mypy` errors recorded in `M36_run1.md` are treated as local tooling drift unless reproduced later.

**Failing gates:**

- **Dependency Review:** unavailable / repo configuration issue (GitHub Advanced Security / dependency graph).
- **Distribution Verification:** HTTP 401 artifact-download issue, known class from M35 (token/permissions).
- **Security Check:** existing `pip-audit` vulnerabilities in the lockfile; not introduced by M36.

M36 remains behavior-preserving and **ready for merge in substance** if branch policy permits; **mergeStateStatus** on the PR may show **UNSTABLE** until those gates pass or are not required. **Public release** remains blocked until supply-chain and infrastructure gate issues are resolved or explicitly documented—route to a dedicated supply-chain / CI recovery milestone, not M36.

**Artifact:** `docs/milestones/M36/M36_pr1_ci_triage.md`

### Merge to `main`

| Field | Value |
| --- | --- |
| **PR** | https://github.com/m-cahill/ezra/pull/37 |
| **Merged** | Yes — squash merge, 2026-05-06 |
| **Merge commit (`main`)** | `969471060c0ad9b528836209531a023c098e5a4e` |
| **Branch protection (API)** | `GET /repos/.../branches/main/protection` returned **404 — Branch not protected** at merge time; PR was **MERGEABLE** despite **UNSTABLE** checks. |
| **Post-merge CI (`main`)** | https://github.com/m-cahill/ezra/actions/runs/25466391573 — **failure** (same non-M36: Dependency Review, Distribution Verification, Security/`pip-audit`; plus SLSA Provenance attestation limitation for private user-owned repo per workflow logs). |

**Record:** `docs/milestones/M36/M36_merge.md`

**Next authorized milestone (sequencing)**

1. **M37B — Required Gate Recovery Implementation** — **closed** — merged via PR #39; see `docs/milestones/M37B/M37B_merge.md`.
2. **M37 — Public Release Boundary Cleanup** — **closed** — merged via PR #40; see `docs/milestones/M37/M37_merge.md`.
3. **M38 — Audit-Polish / Public-Readiness Improvements** — **closed** — merged via PR #41; see `docs/milestones/M38/M38_merge.md`.
4. **M39 — Final Public-Release Audit / Release Readiness Decision** — **closed** — merged via PR #43; record **`docs/milestones/M39/M39_merge.md`**. Optional **M40** (operations/visibility) — see **`docs/ezra.md`**.

**Gate recovery:** **M37A** planning and **M37B** implementation are **complete** on `main`. **M37** secret-boundary cleanup is **complete**. **Do not** conflate **M38** polish with secret-boundary or supply-chain recovery unless a milestone explicitly expands scope.

---

## M37A — Required Gate Recovery for Public Release

**Status:** Closed — merged to `main` via PR #38 (planning complete)

M37A closed as a planning-only milestone. It identified required gate recovery work for public release and preserved all runtime, schema, workflow, dependency, `.gitignore`, and secret-boundary invariants. M37B is authorized for planning as the implementation milestone. M37 public-release boundary cleanup remains deferred until gate recovery is resolved or explicitly accepted.

**Purpose:** Plan recovery for red gates after M36: Security / `pip-audit`, Distribution Verification HTTP 401, Dependency Review, SLSA provenance limits, supplemental Pages/deploy.

**Scope (honored):** Planning only — no runtime, dependency, workflow, schema, `.gitignore`, or secret-cleanup changes.

**Artifacts:** `docs/milestones/M37A/M37A_plan.md`, `docs/milestones/M37A/M37A_run1.md`, `docs/milestones/M37A/M37A_toolcalls.md`, `docs/milestones/M37A/M37A_summary.md`, `docs/milestones/M37A/M37A_audit.md`, `docs/milestones/M37A/M37A_merge.md`.

**PR:** https://github.com/m-cahill/ezra/pull/38

**Record (merge to `main`):** `docs/milestones/M37A/M37A_merge.md`

### M37A Merge to `main`

M37A was merged via PR #38. It closed the planning-only required-gate recovery milestone and seeded M37B. Remaining red checks are known pre-existing gate-recovery targets and are routed to M37B.

M37 remains deferred until M37B resolves or explicitly defers required gate recovery.

Ensure all documentation is updated as necessary.

---

## M37B — Required Gate Recovery Implementation

**Status:** Closed — merged to `main` via PR #39

M37B resolved the actionable default-branch gate recovery issues identified in M37A: `pip-audit` now passes without advisory ignores; Distribution Verification has PR/main `ci-local` behavior and release-artifact verification for release contexts; SLSA and Pages deploy are conditionally honest for the current private user-owned repository; Dependency Review remains a documented infrastructure limitation on pull requests until repository settings support it.

ensure all documentation is updated as necessary

**Purpose:**  
Resolve or honestly defer the red default-branch gates identified by M37A before M37 secret-boundary cleanup.

**Scope:**  
Minimal dependency lockfile recovery, truthful Distribution Verification behavior, SLSA/private-repo honesty, and Pages deploy truthfulness.

**Dependency Review:** PR-only and depends on GitHub Advanced Security / dependency graph availability. Not treated as a primary M37B code fix; workflow keeps **warn-first** behavior unless settings are changed and the check is proven stable on this repo.

**Implementation notes (this milestone):**

- **Track 1:** `pyproject.toml` / `requirements.txt` bumped to clear `pip-audit` without ignores; dev **`types-jsonschema`** for Linux `mypy` parity.
- **Track 2:** PR/main uses `verify_distribution.py --mode ci-local`; full artifact verification uses `workflow_dispatch` input `verify_tag` with `--mode release` and `actions: read`.
- **Track 3:** `actions/attest-build-provenance` runs only when `github.repository_visibility == 'public'`; private repos get a non-failing step summary (CI + Release workflows).
- **Track 4:** `docs-deploy` gated on `vars.EZRA_ENABLE_PAGES_DEPLOY == 'true'`.

**PR:** https://github.com/m-cahill/ezra/pull/39  

**Pre-merge validation (evidence):** run `25469067577` @ `aabfd92987093d0e1d3f81ffbab5adc3f7507a99`; tip run `25469154622` @ `456596c22d78854bc8897a741b9c99f569c4ee45`. See `docs/milestones/M37B/M37B_run1.md`.

**Artifacts:** `docs/milestones/M37B/M37B_plan.md`, `M37B_run1.md`, `M37B_toolcalls.md`, `M37B_summary.md`, `M37B_audit.md`, **`M37B_merge.md`**.

### M37B Merge to `main`

M37B was merged via PR #39. The actionable gate-recovery items identified in M37A were resolved or made truthful: `pip-audit` passes without advisory ignores; Distribution Verification is split into PR/main `ci-local` and release-mode artifact verification; SLSA and Pages deploy are conditional/honest for the current private repo configuration; Dependency Review remains a documented infrastructure limitation until repository settings support it.

M37 — Public Release Boundary Cleanup is now authorized as the next milestone.

ensure all documentation is updated as necessary

| Field | Value |
| --- | --- |
| **Merge SHA (`main`)** | `a51b6c0c731a1d3bc3f34ddc1e71ea240c1062f6` |
| **Post-merge CI (`main`)** | https://github.com/m-cahill/ezra/actions/runs/25470570460 — `conclusion: success` |

**Relationship to M37:** M37 (secret-boundary cleanup) **not** started in M37B; **authorized next** after this merge.

---

## M37 — Public Release Boundary Cleanup

**Status:** Closed — merged to `main` via PR #40

M37 removed only the approved public-release company-secret tracked files under `docs/enhancements/`, confirmed `.cursorrules` and `docs/prompts/` are not tracked, normalized `.gitignore` coverage for all three approved paths, and added a guardrail test preventing reintroduction.

ensure all documentation is updated as necessary

**Purpose:**  
Remove the approved company-secret paths from the committed public repo surface and add a guardrail preventing reintroduction.

**Approved boundary:**

- `.cursorrules`
- `docs/enhancements/`
- `docs/prompts/`

**Scope:**  
M37 removes only tracked files under `docs/enhancements/`, confirms `.cursorrules` and `docs/prompts/` are not tracked, updates `.gitignore`, and adds a public-boundary guardrail test.

**Artifacts:** `docs/milestones/M37/M37_plan.md`, `M37_run1.md`, `M37_toolcalls.md`, `M37_summary.md`, `M37_audit.md`, **`M37_merge.md`**.

### M37 Merge to `main`

M37 was merged via PR #40. The approved company-secret boundary is now absent from Git tracking: `.cursorrules`, `docs/enhancements/`, and `docs/prompts/` return no tracked files via `git ls-files`.

M37 removed only the three tracked `docs/enhancements/*.md` files and added a guardrail test preventing reintroduction. No runtime, EPB schema, dependency, or workflow behavior changed.

M38 — Audit-Polish / Public-Readiness Improvements is **closed** (merged via PR #41). **M39** closed — merged via PR #43 (`docs/milestones/M39/M39_merge.md`); **`GO WITH DOCUMENTED LIMITATIONS`** — see `docs/milestones/M39/M39_public_release_audit.md`.

ensure all documentation is updated as necessary

| Field | Value |
| --- | --- |
| **Merge SHA (`main`)** | `9adfe7a0f789037fe3880a57f1e65cfbd5061f7b` |
| **Post-merge CI (`main`)** | https://github.com/m-cahill/ezra/actions/runs/25473078293 — `conclusion: success` |

---

## M38 — Audit-Polish / Public-Readiness Improvements

**Status:** Closed — merged to `main` via PR #41

**Purpose:** Behavior-preserving public-readiness polish after M37: `CONTRIBUTING.md`, reusable **`docs/release/PUBLIC_RELEASE_CHECKLIST.md`**, README clarity, and manifest **`ezra_version`** resolved from **`importlib.metadata.version("ezra")`** with **`ezra.__version__`** fallback and **`v`‑prefix formatting** to satisfy existing EPB manifest JSON Schema (no schema file edits).

**Scope (summary):** See `docs/milestones/M38/M38_plan.md`. No EPBEmitter extraction, no EPB `epb_version` / hashing / canonicalization changes, no workflow redesign, no dependency bumps, no further secret-boundary removals.

**Artifacts:** `M38_plan.md`, `M38_run1.md`, `M38_toolcalls.md`, `M38_summary.md`, `M38_audit.md`, **`M38_merge.md`**.

**Closeout prompts:** `docs/prompts/summaryprompt.md` and `docs/prompts/unifiedmilestoneauditpromptV2.md` are **absent** (M37 public boundary). Summary/audit follow **M36–M38** structure; missing paths recorded in `M38_summary.md`.

### M38 Merge to `main`

M38 was merged via **PR #41**. It completed behavior-preserving public-readiness polish: contributor guidance, reusable public-release checklist, README clarity, and package-metadata-backed `ezra_version` in EPB manifests while preserving `epb_version` and all EPB schema/canonicalization/hashing invariants.

ensure all documentation is updated as necessary

| Field | Value |
| --- | --- |
| **PR** | https://github.com/m-cahill/ezra/pull/41 |
| **Squash merge SHA (`main`)** | `ab0d07eea5070b57e9112b5b2aecd7e572a8b44a` |
| **Final PR head SHA** | `66d01d98452e7d2fc37b8015a89c89d16f391ef5` |
| **Post-merge CI (`main`)** | https://github.com/m-cahill/ezra/actions/runs/25479475613 — **`conclusion: success`** |
| **PR-only red** | Dependency Review (infra); not introduced by M38 |

---

## M39 — Final Public-Release Audit / Release Readiness Decision

**Status:** Closed — merged to `main` via PR #43

**Purpose:**
Run a fresh current-state public-release audit after M36–M38 reconciliation, gate recovery, boundary cleanup, and public-readiness polish.

**Decision:**
**GO WITH DOCUMENTED LIMITATIONS**

This verdict is based on **current evidence** in `M39_run1.md` and **`M39_public_release_audit.md`**. No historical M33/M35 weighted audit score is asserted or “recovered.”

**Documented limitations (infrastructure / GitHub platform):**

1. **Dependency Review** — Requires GitHub Advanced Security / dependency graph suitable for the repo; CI uses **`continue-on-error: true`** on this job with an explanatory summary. Pull requests may show **failure** on Dependency Review while **`push`** to **`main`** typically **skips** or soft-handles it; **`pip-audit`** remains the strict lockfile audit elsewhere.
2. **SLSA / GitHub artifact attestation** — Workflows document attestation **skipped** or non-persistent for **private** repository classes until visibility/tier supports attestations; README instructs not to claim SLSA attestation success prematurely.
3. **GitHub Pages deploy** — Deploy remains **gated** (repository settings / vars); **Documentation Build** validates docs independent of Pages.

**Scope:**
Planning merged via PR #42 (`docs/milestones/M39/M39_plan_merge.md`). Audit artifacts merged via **PR #43** (squash **`5449b5a`**). Evidence: **`M39_run1.md`**, **`M39_public_release_audit.md`**, **`M39_summary.md`**, **`M39_audit.md`**. Audited content HEAD **`2f782010cecb72856bbf39b5f90b6c526d183d34`** (pre-documentation-only commits on audit branch).

ensure all documentation is updated as necessary

### M39 Plan Merge to `main`

M39 planning was merged via PR #42. The plan defines the final current-state public-release audit and GO / GO WITH DOCUMENTED LIMITATIONS / NO-GO decision criteria.

| Field | Value |
| --- | --- |
| **PR** | https://github.com/m-cahill/ezra/pull/42 |
| **Final head SHA** | `34035f3c1679e0d89803038322855bb0c6876310` |
| **Squash merge SHA (`main`)** | `bd8a27ffef8366d9a430e8f583bbba8ea12a4239` |
| **Post-merge CI (`main`)** | https://github.com/m-cahill/ezra/actions/runs/25481653532 — **`conclusion: success`** |
| **PR-only red** | Dependency Review on PR #42 (infra); post-merge `main` — Dependency Review **skipped** |

**Record:** `docs/milestones/M39/M39_plan_merge.md`

### M39 Audit execution

| Field | Value |
| --- | --- |
| **Audit completion PR** | https://github.com/m-cahill/ezra/pull/43 |
| **Audited HEAD** | `2f782010cecb72856bbf39b5f90b6c526d183d34` |
| **Completion branch** | `audit/m39-final-public-release-audit` |
| **Evidence pack** | `M39_run1.md`, `M39_public_release_audit.md`, `M39_summary.md`, `M39_audit.md` |
| **Latest `main` CI referenced** | https://github.com/m-cahill/ezra/actions/runs/25483563138 — **`conclusion: success`** (post-merge PR #43 squash to `main`) |

### M39 Merge to `main`

M39 was merged via PR #43. It completed the final current-state public-release audit and returned:

**GO WITH DOCUMENTED LIMITATIONS**

No NO-GO issues were found on audited HEAD `2f782010cecb72856bbf39b5f90b6c526d183d34`.

Documented limitations:

- Dependency Review requires GHAS / dependency graph support.
- SLSA artifact attestation is limited while the repository is private / user-owned.
- Pages deploy is gated; docs build remains validated.

Human maintainer may proceed with public-release operational steps or authorize a dedicated M40 release/visibility milestone.

ensure all documentation is updated as necessary

**Record:** `docs/milestones/M39/M39_merge.md`

---

## M40 — Public Release Operation / Visibility Decision

**Status:** Planning complete — pending merge review

**Purpose:**

Plan the operational step after M39’s **`GO WITH DOCUMENTED LIMITATIONS`** decision: repository visibility for **`m-cahill/ezra`**, optional tag/release orchestration **after** explicit approval, post-operation evidence, limitation carry-forward, and governance-oriented release-notes / announcement checklist (no marketing draft unless explicitly requested).

**Scope:**

Planning only. No visibility, tag, release, PyPI publish, Pages enablement, runtime, dependency, workflow, EPB spec, secret-boundary, or `docs/prompts/` changes.

**Preferred path:** make public **after** explicit maintainer approval, with fallback **keep private** (ready-when-triggered). **Visibility-first;** tag/release only if separately authorized; do not assume tag name; do not reuse historical milestone tags as the public announcement artifact without maintainer decision.

**Artifacts:** `docs/milestones/M40/M40_plan.md`, `docs/milestones/M40/M40_toolcalls.md`, `M40_summary.md`, `M40_audit.md`.

**PR:** https://github.com/m-cahill/ezra/pull/44

M40 documents the public-release operation path after M39’s **`GO WITH DOCUMENTED LIMITATIONS`** decision. It preserves a **human approval gate** before any repository visibility, tag, GitHub Release, PyPI, Pages, or settings operation.

**No operational release action was performed** in M40 planning.

ensure all documentation is updated as necessary
