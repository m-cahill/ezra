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

1. **M37B — Required Gate Recovery Implementation** — see `docs/milestones/M37B/M37B_plan.md`.
2. **M37 — Public Release Boundary Cleanup** — after M37B or explicit acceptance of remaining reds; remove user-approved company-secret paths from Git tracking (where still applicable), add ignore rules, and guardrails against reintroduction.

**Gate recovery:** **M37A** (planning) is **closed** — see M37A section below. **M37B** carries implementation per `docs/milestones/M37B/M37B_plan.md`. **Do not** conflate **M37** secret cleanup with supply-chain CI recovery.

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

**Status:** Implementation complete — Pending merge review (PR #39)

M37B resolved the actionable default-branch gate recovery issues identified in M37A: `pip-audit` now passes without advisory ignores; Distribution Verification has PR/main `ci-local` behavior and release-artifact verification for release contexts; SLSA and Pages deploy are conditionally honest for the current private user-owned repository; Dependency Review remains a documented infrastructure limitation.

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
**Tip CI (authoritative for merge review):** run `25468576713`, head `e9079b6558d65eb667ab82882a7c9237c27a1a02` — workflow **success**; only **Dependency Review** fails (settings/GHAS).

**Artifacts:** `docs/milestones/M37B/M37B_plan.md`, `M37B_run1.md`, `M37B_toolcalls.md`, `M37B_summary.md`, `M37B_audit.md`.

**Relationship to M37:** M37 (secret-boundary cleanup) **not** started in M37B; after PR #39 merges, M37 may proceed per sequencing.
