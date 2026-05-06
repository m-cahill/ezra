# EZRA Refactor Ledger

This document is the authoritative refactor-program ledger for public-release readiness work from M36 onward.

`docs/ezra.md` remains the canonical project governance and architecture ledger. This file records refactor-specific milestone decisions, audit reconciliation outcomes, public-release boundary decisions, and follow-up hooks.

---

## M36 — Audit Reconciliation & Public Release Boundary Inventory

**Status:** Closed — Proceed to M37

**Summary:**

M36 reconciled the M33/Post-M32 full audit (`docs/M33fullaudit.md`, commit `23789314ba5f6a502c650f6a098f12eb4ed0e8b4`, weighted score **4.95**) against the M35/current full audit (external planning artifact at commit `f12fd083b1b0e9f9c518535e0938b65d204b5075`, weighted score **4.40**). The **−0.55** overall delta is assessed as **primarily audit calibration drift and public-release-readiness polish**, not a true project regression: Architecture, Tests & CI, and Security remained **5/5** in both audits; deltas concentrate on Modularity, Code Health, Performance, DX, and Docs where the later audit applied a stricter consumer-facing lens without contradicting M33’s factual claims.

**Secret-boundary inventory** (command `git ls-files .cursorrules docs/enhancements docs/prompts` at M36 closeout): only `docs/enhancements/` files were listed as tracked; `.cursorrules` and `docs/prompts/` had **no** tracked paths at that moment. **Historical note:** `git diff 23789314..HEAD` shows `.cursorrules` and former `docs/prompts/**` paths as removed in that interval—i.e. the repo already moved those out of Git in later work; M36 performed **no** cleanup. M37 remains authorized to add ignore/guardrails for all three user-approved paths.

**Evidence artifacts:** `docs/release/AUDIT_RECONCILIATION_M33_M35.md`, `docs/milestones/M36/M36_plan.md`, `docs/milestones/M36/M36_run1.md`, `docs/milestones/M36/M36_summary.md`, `docs/milestones/M36/M36_audit.md`.

**M36 constraints honored:** No changes under `src/ezra/`, no EPB schema/spec edits, no `.github/workflows/**` edits, no dependency or `.gitignore` edits, no secret untracking in M36.

### PR #37 CI triage

PR #37 CI run `25465492721` failed on pre-existing or infrastructure-related checks, not on M36 documentation changes. Type Check passed on Linux CI, so the local Windows `mypy` errors recorded in `M36_run1.md` are treated as local tooling drift unless reproduced later.

**Failing gates:**

- **Dependency Review:** unavailable / repo configuration issue (GitHub Advanced Security / dependency graph).
- **Distribution Verification:** HTTP 401 artifact-download issue, known class from M35 (token/permissions).
- **Security Check:** existing `pip-audit` vulnerabilities in the lockfile; not introduced by M36.

M36 remains behavior-preserving and **ready for merge in substance** if branch policy permits; **mergeStateStatus** on the PR may show **UNSTABLE** until those gates pass or are not required. **Public release** remains blocked until supply-chain and infrastructure gate issues are resolved or explicitly documented—route to a dedicated supply-chain / CI recovery milestone, not M36.

**Artifact:** `docs/milestones/M36/M36_pr1_ci_triage.md`

**Next authorized milestone:**

**M37 — Public Release Boundary Cleanup** — Remove only the user-approved company-secret paths from Git tracking (where still applicable), add ignore rules, and guardrails against reintroduction. Do not begin M37 until M36 is accepted on `main`.
