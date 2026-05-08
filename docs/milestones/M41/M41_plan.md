# M41 — Public Repo Post-Visibility Smoke

**Status:** Planning only (this deliverable)  
**Repository:** `m-cahill/ezra` — **public** at https://github.com/m-cahill/ezra  
**M39 decision (preserved):** **GO WITH DOCUMENTED LIMITATIONS** (`docs/milestones/M39/M39_public_release_audit.md`)

M40 completed a **visibility-only** public step; **tag**, **GitHub Release**, **PyPI**, and **Pages** remain **deferred**. M41 plans a **small post-visibility smoke** to observe **public pull-request CI** and capture **Dependency Review** (and optionally **SLSA**-related job behavior) **without** releasing.

**Planning-only rule:** This milestone’s **current** deliverables are `M41_plan.md`, `M41_toolcalls.md`, and governance updates. **Do not** open the smoke PR or change `main` until **M41 execution** is explicitly authorized on branch **`docs/m41-post-visibility-smoke`**.

---

## 1. Intent / Target

**Objective:** After the repository became public (M40), plan a **docs-only** change set merged via a **normal public PR** so the project can:

- Observe **full public PR lifecycle** (checks, merge, post-merge `main` CI).
- **Record actual Dependency Review behavior** on a public repo PR — **do not** assume it starts working automatically; possibilities include success, continued failure (GHAS / dependency-graph class), skip, or other behavior — capture logs and `gh pr checks` output.
- Optionally note whether any workflow step tied to **SLSA / attestation** runs differently on public PRs; **full** attestation proof may still require a **later** workflow path (e.g. release or dedicated run) — M41 documents what ran, without claiming universal SLSA success.
- Re-verify **public release boundary** remains clean (`git ls-files` for boundary paths).
- Keep **M39 documented limitations** honest; update governance only with **observed** facts.

**Target outcome:** Maintainer merges a **small, meaningful docs-only** PR if checks are acceptable, with evidence in `M41_run1.md` (and follow-on summary/audit per closeout). **No** release artifacts.

---

## 2. Scope Boundaries

### In scope (execution phase, when authorized)

- Open **`docs/m41-post-visibility-smoke`** from current `main`.
- Make a **small meaningful documentation change** only, for example:
  - a milestone / governance clarification in `REFACTOR.md` or `docs/ezra.md`,
  - or a concise `docs/milestones/M41/M41_run1.md` evidence stub filled during the smoke run,
  - or a minor **README** / **`docs/release/PUBLIC_RELEASE_CHECKLIST.md`** wording fix **only if** it clearly helps the public smoke narrative.
- Run **local preflight** before push (align with M40 visibility discipline: Ruff, format, mypy, pytest, `pip-audit`, `ci-local` distribution verification as documented in repo practice / checklists).
- Open **one PR**; observe **all checks**; record **Dependency Review** conclusion and any **mergeability / mergeStateStatus** quirks (e.g. `UNSTABLE`).
- **Merge the PR** if checks pass from a maintainer perspective (same as M40 guidance: do not abandon a healthy PR without cause). **Goal:** post-merge **`main` CI** URL captured in evidence.
- Re-run **boundary** check; confirm **empty**.
- Update **governance** (`REFACTOR.md`, `docs/ezra.md`) and add/complete **`M41_run1.md`**, **`M41_summary.md`**, **`M41_audit.md`**, **`M41_merge.md`** as execution completes.

### Out of scope

- **No** new **tag**, **GitHub Release**, **PyPI publish**, **Pages** enablement, or **`EZRA_ENABLE_PAGES_DEPLOY`** changes.
- **No** GitHub **repo settings** or **branch protection** edits unless a **separate** milestone authorizes them.
- **No** `.github/workflows/**` edits unless a **public-visibility defect** is found and a **separate fix** is explicitly authorized.
- **No** `src/ezra/**` (runtime), **`pyproject.toml` / `requirements.txt`**, **`docs/specs/epb_v1/**`**, or **secret-boundary** mutations.
- **No** restoration of **`docs/prompts/`** to the tracked surface.
- **No** claim that M39 limitations are **fully** resolved based on this smoke alone.

---

## 3. Invariants

| Invariant | Verification |
|-----------|----------------|
| M39 posture preserved | Ledger text remains **GO WITH DOCUMENTED LIMITATIONS** where applicable |
| Docs-only smoke PR | Diff contains **no** runtime, workflow, dependency, EPB spec, or boundary-path adds |
| Boundary clean | `git ls-files .cursorrules docs/enhancements docs/prompts` → **empty** before and after merge |
| No unapproved release ops | No `git tag`, `gh release create`, PyPI publish, `gh repo edit` visibility, Pages enable |
| Honest Dependency Review | **Observe and record**; do not assume GHAS/graph availability |

---

## 4. Verification Plan

### 4.1 Preflight (before opening smoke PR)

- Clean tree; intended docs edits only.
- Boundary command above → empty.
- Local / maintainer checks per project norms (Ruff, format, mypy, pytest, `pip-audit`, distribution `ci-local` mode).

### 4.2 PR observation

- `gh pr view <n> --json state,mergeable,mergeStateStatus,statusCheckRollup,headRefOid,url`
- `gh pr checks <n>` (or equivalent) — screenshot or paste **Dependency Review** line item.
- Capture **merge SHA** and **post-merge `main` CI** run URL(s).

### 4.3 Dependency Review (expectations)

Plan for **three classes** of outcomes; record **which occurred**:

1. **Passes / useful signal** — document; maintainer may later treat as stable enough to tighten policy (outside M41 unless authorized).
2. **Fails** — align with known **GHAS / dependency-graph** limitation; no workflow change in M41 unless separate approval.
3. **Skips or differs** — document exact behavior (job name, conclusion, log snippet).

### 4.4 SLSA / attestation (secondary)

- If **CI** exposes an attestation or provenance step on the **PR** run, note pass/fail/skip and URL.
- If **not** exercised on PRs, **do not** claim failure — state **not observed on this PR**; optional follow-up remains a **release** or **workflow_dispatch** path (defer to maintainer / later milestone).

### 4.5 Post-merge

- Confirm latest `main` CI **success** for required jobs (record exceptions if policy allows merge with known flakes — default: **green** before calling smoke complete).

---

## 5. Implementation Steps

1. **Authorize execution** — Maintainer confirms M41 smoke (planning-only phase ends).
2. **Branch** — `git checkout main && git pull --ff-only && git checkout -b docs/m41-post-visibility-smoke`.
3. **Edit** — Apply **one coherent docs-only** change (meaningful, merge-worthy if green).
4. **Preflight** — Local commands; boundary check.
5. **Commit & push** — Single focused commit or minimal series; **no** tag.
6. **PR** — Open against `main`; title/description state **M41 post-visibility smoke**; link `M41_plan.md`.
7. **Observe** — Record check rollup; emphasize Dependency Review; wait for **merge** decision.
8. **Merge** (if acceptable) — Prefer **squash** subject line agreed with ledger style, e.g. `docs(m41): post-visibility public PR smoke`.
9. **Evidence** — Fill `M41_run1.md` with URLs, SHAs, boundary output, Dependency Review outcome class.
10. **Closeout** — `M41_summary.md`, `M41_audit.md`, `M41_merge.md`; update `REFACTOR.md`, `docs/ezra.md`.
11. **Stop** — Do **not** start M42 (tag/release) unless separately authorized.

---

## 6. Risk & Rollback Plan

| Risk | Mitigation |
|------|-------------|
| Dependency Review blocks merge | Treat as **observation**; document; do **not** change workflows in M41 without separate approval; maintainer may merge if branch policy allows despite soft-fail (match M40 precedent only if still true) |
| Unexpected CI failure on docs | Reproduce locally; fix **docs only** if trivial; if infrastructure, document and stop rather than widening scope |
| Accidental scope creep (code/workflow) | Reject; revert non-docs changes; stay on `docs/m41-post-visibility-smoke` only |
| Overclaims in closeout | Tie every statement to a URL or command output |

**Rollback:** For docs-only PR, revert or forward-fix with another docs PR; **no** tag or release to unwind.

---

## 7. Deliverables

### Planning (this cycle — complete when PR for plan merges)

- `docs/milestones/M41/M41_plan.md` (this file)
- `docs/milestones/M41/M41_toolcalls.md`
- Updated `REFACTOR.md` (M41 section)
- Updated `docs/ezra.md` (M41 row)

### Execution (when authorized — not part of this planning-only commit)

- Branch `docs/m41-post-visibility-smoke` with merged smoke PR
- `docs/milestones/M41/M41_run1.md` (required evidence)
- `M41_summary.md`, `M41_audit.md`, `M41_merge.md`
- Governance updates reflecting **observed** public PR behavior

---

## 8. Explicit Non-Goals

- Formal **version tag** or **GitHub Release** (→ **M42** or later, separate authorization).
- **PyPI** publish.
- **Pages** production deploy enablement.
- **Workflow**, **dependency**, **runtime**, **EPB** spec, **secret-boundary**, or **repo settings** changes **as part of M41**, except a **separately approved** defect fix.
- Resolving **all** M39 limitations in one smoke milestone.

---

## 9. Closeout Instructions

When M41 **execution** completes:

1. Use **`docs/prompts/summaryprompt.md`** and **`docs/prompts/unifiedmilestoneauditpromptV2.md`** **if present** in the workspace.
2. **If absent** (expected: these paths are **not** in-repo per M37 boundary — record **missing paths** in `M41_run1.md` or `M41_summary.md`) and follow **M36–M40** artifact patterns for summary and audit.
3. Ensure **`REFACTOR.md`** and **`docs/ezra.md`** reflect M41 completion, PR link, merge SHA, and key observation (**Dependency Review** class).
4. Include in closeout artifacts:

```text
ensure all documentation is updated as necessary
```

---

ensure all documentation is updated as necessary
