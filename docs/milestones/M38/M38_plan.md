# M38 — Audit-Polish / Public-Readiness Improvements (plan)

## Note

M38 is a small, **behavior-preserving** documentation and developer-experience milestone. It closes low-risk Docs/DX/Code Health polish called out by the M35 audit (without chasing a numeric audit score). It does **not** change EPB schema, hashing, canonicalization, or runtime perception behavior.

**Confirmed inventory:** `src/ezra/epb/builder.py` still embeds `"ezra_version": "v0.0.8-m07"` with `# TODO: Get from package metadata` — this is the primary Code Health / correctness gap for package-version alignment.

## 1. Intent / target

Recover **public-readiness confidence** by:

- Adding a practical, repo-specific **`CONTRIBUTING.md`** (EZRA governance tone: formal, concise, audit-ready, contributor-friendly).
- Adding a **reusable** **`docs/release/PUBLIC_RELEASE_CHECKLIST.md`** for pre-release verification (including first public release notes where relevant).
- Polishing **`README.md`** for public-facing clarity (what EZRA is / is not, quickstart, verification, EPB–RediAI artifact boundary, security and CI honesty — no marketing or supply-chain overclaims).
- Planning and (in implementation) fixing **hardcoded / stale `ezra_version` in EPB manifest construction** via `importlib.metadata.version("ezra")` with a safe fallback, plus tests so EPB manifest behavior stays correct and deterministic where required.

**Audit posture:** Prepare evidence for a **new** final public-release audit. Do **not** claim restoration of any historical weighted score until an audit says so.

## 2. Scope boundaries

**In scope:**

- Root **`CONTRIBUTING.md`**: local setup; standard verification commands (`ruff`, `mypy`, `pytest`, optional parity/integration env vars); plugin add/change pointers (registry, tests, parity policy); EPB/schema invariant references; public-release boundary rules (`tests/test_public_release_boundary.py`, `git ls-files` checks); PR checklist.
- **`docs/release/PUBLIC_RELEASE_CHECKLIST.md`**: secret-boundary check; default-branch CI trust; `pip-audit`; distribution verification modes (`ci-local` vs release/tag); docs build (if applicable); EPB schema non-drift; README/CONTRIBUTING presence; honest notes on SLSA / Dependency Review limits; pointer to final public-release audit.
- **`README.md`** edits: general clarity; links to `CONTRIBUTING.md`, `docs/VISION.md`, `docs/ezra.md`, and the public release checklist.
- **Version metadata:** targeted search under `src/ezra/`, `tests/`, `pyproject.toml`, `docs/` as needed; implement builder (and any other) fixes per implementation phase.

**Out of scope (explicit):**

- EPBEmitter extraction; broad runtime refactors; EPB schema or `epb_version` contract changes; workflow redesign; dependency bumps unless **required** by current CI failure; further secret-boundary or `.gitignore` changes beyond documenting existing rules; removing additional tracked files; Contributor Covenant / DCO / CLA / new legal contributor policy (unless a pointer to an **existing** repo doc is discovered — none expected).

## 3. Invariants

| Invariant | Check |
| --- | --- |
| No EPB contract drift | No edits under `docs/specs/epb_v1/**` except if a doc typo is unavoidable and does not change normative meaning — prefer README/CONTRIBUTING only |
| `epb_version` field in bundles | Immutable per governance; only **emitter metadata** such as `ezra_version` may change source of truth |
| CI truthfulness | No `continue-on-error` weakening on required checks; no newly muted failures |
| Behavior preservation | Full test suite green; determinism / golden baselines unaffected unless a version string in manifest is intentionally aligned (document in run artifact) |
| Public-release boundary | `git ls-files .cursorrules docs/enhancements docs/prompts` remains empty; guardrail test still passes |

## 4. Verification plan

- Local: `ruff check .`, `ruff format --check .`, `mypy src`, `pytest` (and `pip-audit -r requirements.txt`, `python scripts/verify_distribution.py --mode ci-local` per local/M37B practice).
- Confirm **`ezra_version`** in emitted manifest reflects installed package version (or documented fallback) after implementation — extend or add tests if manifest content is snapshot-tested.
- PR CI: expect green required jobs on default workflow; Dependency Review may remain PR/infrastructure-limited per M37B — document in run log if observed.
- Optional manual: reread README for forbidden claims (training, RediAI runtime integration, SLSA guarantees on private repos).

## 5. Implementation steps

1. Land this plan and tool log; update `REFACTOR.md` and `docs/ezra.md` milestone row.
2. Draft **`CONTRIBUTING.md`** per scope; cross-link from README.
3. Add **`docs/release/PUBLIC_RELEASE_CHECKLIST.md`** (reusable checklist + initial-public-release subsection).
4. Polish **`README.md`** (structure, boundaries, links — no overclaims).
5. Grep for stale version / TODO patterns (`ezra_version`, `Get from package metadata`, etc.); implement **`importlib.metadata`-based** resolution in `src/ezra/epb/builder.py` (and elsewhere only if discovered) with safe fallback; update **`pyproject.toml` / `__init__.py`** only if needed for consistency.
6. Adjust tests if manifest expectations change; run full local verification.
7. Open PR to `main`; monitor CI; record **`M38_run1.md`** (and increments if needed).
8. Closeout (after permission): summary, audit, merge record; **ensure all documentation is updated as necessary.**

## 6. Risk & rollback plan

**Risk:** Low-to-medium. README/CONTRIBUTING-only edits are low risk. Changing `ezra_version` source may affect golden or snapshot tests that pin manifest strings — mitigate by scoped test updates and explicit run documentation.

**Rollback:** Revert the merge commit or PR branch; no schema migrations or data transforms involved.

## 7. Deliverables

| Artifact | Purpose |
| --- | --- |
| `M38_plan.md` | This document |
| `M38_toolcalls.md` | Tool/command log per milestone discipline |
| `M38_runN.md` | CI and command evidence |
| `M38_summary.md`, `M38_audit.md`, `M38_merge.md` | Closeout (after implementation) |
| `CONTRIBUTING.md` | Contributor onboarding and PR discipline |
| `docs/release/PUBLIC_RELEASE_CHECKLIST.md` | Reusable release checklist |
| Updated `README.md` | Public-facing clarity |
| Code/test updates | Canonical `ezra_version` (and any siblings found) |
| `REFACTOR.md`, `docs/ezra.md` | Governance sync |

## 8. Explicit non-goals

- EPBEmitter extraction and large-scale refactors.
- EPB schema, hashing, or canonicalization rule changes.
- Workflow redesign; dependency updates except CI-driven necessity.
- Additional secret-boundary file removals or policy expansion beyond documentation of current rules.
- Legal contributor frameworks (CoC, DCO, CLA) unless pre-existing in repo.

---

## Closeout instructions (for later)

- If **`docs/prompts/summaryprompt.md`** and **`docs/prompts/unifiedmilestoneauditpromptV2.md`** exist, use them for summary and audit generation.
- **Current repo state:** those paths are **not** present under `docs/prompts/` (removed from public surface per M37). Record their absence in `M38_summary.md` / `M38_audit.md` and use the **established M36–M37 structure** (`M37_summary.md`, `M37_audit.md`, `REFACTOR.md` merge sections as style references).
- **ensure all documentation is updated as necessary.**
