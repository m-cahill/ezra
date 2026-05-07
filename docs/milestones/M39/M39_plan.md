# M39 — Final Public-Release Audit / Release Readiness Decision (plan)

## 1. Intent / target

Produce a **fresh, current-state** public-release audit of the repository **after** M36–M38 (audit reconciliation, required-gate recovery, public-release boundary cleanup, and public-readiness polish). From that evidence, record an explicit release readiness outcome:

- **GO**
- **GO WITH DOCUMENTED LIMITATIONS**
- **NO-GO**

**Do not** assume or cite historical weighted audit scores from M33, M35, or earlier milestones as substitutes for this audit. M39’s verdict must rest on **commands, CI state, and doc review performed during M39 execution**, recorded in `M39_audit.md` (and supporting run artifacts when execution begins).

This document is **planning only**. The final audit run is **not** started in the PR that lands this plan.

---

## 2. Scope boundaries

**In scope (execution phase, after plan approval):**

- Evidence gathering: local commands, `gh` CI inspection, targeted documentation review for overclaims.
- Classification of outcomes per §7.
- Written audit artifact (`M39_audit.md`) and summary (`M39_summary.md`) at closeout.

**Out of scope for M39 (unless a separate milestone authorizes it):**

- Runtime (`src/ezra/**`), tests beyond running them as verification, workflow (`.github/workflows/**`), dependency / lockfile edits, EPB spec/schema (`docs/specs/epb_v1/**`), secret-boundary file removals or restores, adding `docs/prompts/**`.
- Making an actual **PyPI tag release** or changing Trusted Publishing configuration.

**This planning PR:**

- Adds only `docs/milestones/M39/M39_plan.md`, `docs/milestones/M39/M39_toolcalls.md`, and governance updates to `REFACTOR.md` and `docs/ezra.md`.

---

## 3. Invariants

Preserve unless a **future** milestone explicitly changes them:

| Invariant | Meaning |
| --- | --- |
| CI truthfulness | Required gates reflect real pass/fail; no silent muting of failures |
| Public-release boundary | `.cursorrules`, `docs/enhancements`, `docs/prompts` remain **untracked**; guardrail test continues to enforce |
| EPB contract | No unintended drift under `docs/specs/epb_v1/**`; `epb_version` remains **1.0.0**; canonicalization and hashing rules unchanged |
| Honest supply-chain / infra claims | Dependency Review, SLSA, Pages, and similar are described accurately for this repo’s settings |
| Artifact-boundary-only RediAI posture | No documentation or code claims of runtime integration with RediAI |

---

## 4. Audit inputs

Use the **current tree** at M39 execution time (expected baseline: `main` after M38 merge and governance commits). Reference context from:

| Artifact | Present? | Notes |
| --- | :---: | --- |
| `docs/M33fullaudit.md` | Yes | Historical full audit; context only — **not** the M39 score |
| `docs/release/AUDIT_RECONCILIATION_M33_M35.md` | Yes | Reconciliation narrative; informs honest-claims review |
| `docs/release/PUBLIC_RELEASE_CHECKLIST.md` | Yes | Checklist to mirror during audit |
| `docs/milestones/M36/M36_merge.md` | Yes | M36 closeout / sequencing |
| `docs/milestones/M37A/M37A_merge.md` | Yes | Gate recovery planning record |
| `docs/milestones/M37B/M37B_merge.md` | Yes | Gate recovery implementation record |
| `docs/milestones/M37/M37_merge.md` | Yes | Boundary cleanup record |
| `docs/milestones/M38/M38_merge.md` | Yes | Public-readiness polish; `ezra_version` metadata fix |
| `REFACTOR.md` | Yes | Refactor ledger M36–M38 |
| `docs/ezra.md` | Yes | Canonical governance / milestone index |
| `README.md` | Yes | Primary public-facing surface |
| `CONTRIBUTING.md` | Yes | Contributor onboarding |
| `docs/release/DISTRIBUTION_VERIFICATION.md` | Yes | Distribution verification modes and expectations |

**Planning verification (2026-05-07):** All paths above exist locally; **no** audit input gaps for planned execution.

**Closeout prompt paths (for later):**

| Path | Present? |
| --- | :---: |
| `docs/prompts/summaryprompt.md` | No |
| `docs/prompts/unifiedmilestoneauditpromptV2.md` | No |

Record absence in `M39_summary.md` / `M39_audit.md` and follow **M36–M38** milestone artifact structure for prose.

---

## 5. Verification plan

During **audit execution**, run (and paste or link evidence for) at minimum:

```bash
git status --short
git rev-parse HEAD
git ls-files .cursorrules docs/enhancements docs/prompts
ruff check .
ruff format --check .
mypy src
pytest -q
pip-audit -r requirements.txt
python scripts/verify_distribution.py --mode ci-local
gh run list --branch main --limit 5
```

**Optional** (signal-only; interpret per §2 of original milestone guidance — hits inside historical milestone records are not automatic failures unless they reflect active public guidance or tracked secrets):

```bash
grep -R "v0\.0\.8-m07\|Get from package metadata\|docs/enhancements\|docs/prompts\|\.cursorrules" -n README.md docs src tests pyproject.toml || true
```

**Windows note:** Prefer `rg` or PowerShell `Select-String -Path ... -Pattern ...` if `grep -R` is unavailable; record the equivalent command in the audit.

---

## 6. Audit execution plan

Execute **after** this plan merges and an implementer is authorized.

1. **Sync** to audited SHA; record `git rev-parse HEAD` and clean working tree (or document intentional dirt).
2. **Public-release boundary** — Confirm `git ls-files .cursorrules docs/enhancements docs/prompts` is empty; run `pytest -q tests/test_public_release_boundary.py` (or full suite); confirm no private prompt/enhancement paths reintroduced as tracked files.
3. **Default-branch CI trust** — Use `gh run list` / `gh run view` on latest `main` runs; confirm green required jobs; confirm Dependency Review limitation is documented and not misrepresented as universal green on PRs; scan workflows mentally or via doc cross-check that required gates are not `continue-on-error`-muted.
4. **Supply chain** — `pip-audit -r requirements.txt`; confirm SBOM/provenance jobs remain coherent with README/checklist (no success theater).
5. **Distribution verification** — `python scripts/verify_distribution.py --mode ci-local` passes locally; cross-read `DISTRIBUTION_VERIFICATION.md` and checklist for release vs CI-local modes; confirm no stale “HTTP 401 passes as green” story on default CI if that was the historical failure mode (M35-era — verify current truth).
6. **EPB non-drift** — `git diff` / history scan for unintended edits under `docs/specs/epb_v1/**`; confirm `epb_version` constant remains **1.0.0** in spec and emission paths; treat **`ezra_version`** as non-contract producer metadata (document per M38).
7. **Docs / DX public readiness** — README, CONTRIBUTING, checklist, `docs/ezra.md`, `REFACTOR.md` current and consistent.
8. **Honest claims pass** — Explicit checklist:
   - No “training in EZRA” claims
   - No RediAI **runtime** integration claims (artifact boundary only)
   - No SLSA “success” unless attestation actually ran and succeeded for the context claimed
   - No performance guarantees without measurements
   - No “audit score recovered” without **this** audit’s evidence
9. **Record** outcomes and commands in `M39_run1.md` (if CI/command iterations needed, increment). Produce `M39_audit.md` and `M39_summary.md` at closeout.

---

## 7. Release readiness decision criteria

### GO

Choose **only** if:

- Default-branch CI is **green** on required gates for the audited HEAD (or immediately prior documented green with explained SHA equivalence).
- Public-release boundary is clean (§6.2).
- Security checks pass including **`pip-audit`** (§6.4).
- Distribution verification is **truthful** for documented modes (§6.5).
- No EPB contract drift (§6.6).
- README / CONTRIBUTING / checklist present and accurate (§6.7).
- No release-blocking overclaims (§6.8).

### GO WITH DOCUMENTED LIMITATIONS

Choose if **only** documented, non-blocking infrastructure constraints remain, for example:

- Dependency Review unavailable on PRs without GHAS / dependency graph — **documented**, not hidden.
- SLSA attestation skipped or non-applicable while repo is private / user-owned — **honestly** framed.
- GitHub Pages deploy disabled by repo setting while docs build remains green — **documented**.

Limitations must appear in the audit narrative and in public-facing docs where users would be misled otherwise.

### NO-GO

Choose if **any** of:

- Secrets or approved boundary paths are **tracked**.
- Required CI is **red** or failures are masked.
- **`pip-audit`** fails on `requirements.txt`.
- EPB schema / canonicalization / hashing **drift** detected without approved version bump.
- README or docs contain **misleading** release or security claims.
- Distribution verification is **broken** or presents a **false green**.

---

## 8. Risk & rollback plan

**Risks:**

- **False confidence** from stale CI or local-only green — mitigate by pinning evidence to SHA + run URLs.
- **Interpretation drift** on optional checks — mitigate by aligning verdict language with §7.
- **Scope creep** into code/workflow fixes — route those to M40+; M39 remains evidence and decision.

**Rollback:** This milestone is documentation-bound. If the plan is wrong, revise via a follow-up docs PR; no runtime rollback required.

---

## 9. Deliverables

| Deliverable | When |
| --- | --- |
| `M39_plan.md` | Planning PR (this file) |
| `M39_toolcalls.md` | Planning PR |
| Updated `REFACTOR.md`, `docs/ezra.md` | Planning PR |
| `M39_run1.md` (etc.) | Execution phase — command/CI evidence |
| `M39_audit.md`, `M39_summary.md` | Closeout |
| `M39_merge.md` | After merge record (per prior milestones) |

---

## 10. Explicit non-goals

- Running the **final** audit in the same PR as this plan.
- Claiming a **final public-release weighted score** without a dedicated audit methodology for M39.
- Emitting release **GO / NO-GO** in planning PR prose as if decided (plan describes **how**; execution decides).
- Recreating missing inputs — if something disappears later, record as **audit input gap**, do not invent files.

---

## 11. Closeout instructions

When M39 **execution** completes and merge is authorized:

1. Create **`docs/milestones/M39/M39_summary.md`** and **`docs/milestones/M39/M39_audit.md`**.
2. Prefer prompts **`docs/prompts/summaryprompt.md`** and **`docs/prompts/unifiedmilestoneauditpromptV2.md`** if they exist; **currently they do not** — use **M36–M38** milestone summaries/audits as structural references and state missing paths explicitly.
3. Update **`REFACTOR.md`** and **`docs/ezra.md`** with M39 completion, PR link, merge SHA, and verdict summary.
4. **ensure all documentation is updated as necessary**
5. Do **not** add **`docs/prompts/`** unless explicitly authorized.

---

## Reference — authorized context (pre–M39 execution)

- M38 merge SHA (squash): `ab0d07eea5070b57e9112b5b2aecd7e572a8b44a`
- Governance record on `main` (ledger): `98d81a00889c7696e3b7cbb6e14991deec25950e` (per pre-plan branch tip; re-verify at execution time)
