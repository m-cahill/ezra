# M36_run1 — Repository inventory & local verification

**Milestone:** M36 — Audit Reconciliation & Public Release Boundary Inventory  
**Date:** 2026-05-06  
**Runner:** Cursor (local)  
**HEAD:** `f12fd083b1b0e9f9c518535e0938b65d204b5075`

---

## 1. Git repository inventory

### `git status --short`

```text
(clean — no output)
```

`git status --short` was captured **before** M36 artifact creation and staging; the final staged diff for M36 should be limited to the documentation and governance files listed in §4.

### Current HEAD

```text
f12fd083b1b0e9f9c518535e0938b65d204b5075
```

### Company-secret path inventory

**Command:**

```bash
git ls-files .cursorrules docs/enhancements docs/prompts
```

**Output (exact):**

```text
docs/enhancements/AuditEnhancementsV2.md
docs/enhancements/EnhancementsV2.md
docs/enhancements/TestingEnhancementsV2.md
```

**Note:** At M36 inventory time, **no** tracked paths under `.cursorrules` or `docs/prompts/`. Historical diff (below) shows `.cursorrules` and `docs/prompts/**` removed between the M33 baseline commit and HEAD—i.e. they are already absent from the index at HEAD.

---

## 2. Diff vs M33 baseline

**Baseline commit:** `23789314ba5f6a502c650f6a098f12eb4ed0e8b4`

### `git diff --stat 23789314ba5f6a502c650f6a098f12eb4ed0e8b4..HEAD`

```text
 .cursorrules                                      | 206 ------
 .github/workflows/ci.yml                          |  40 ++
 .github/workflows/release.yml                     |  33 +
 .gitignore                                        |   6 +
 .pre-commit-config.yaml                           |   5 +-
 README.md                                         |  61 ++
 docs/CI_ARCHITECTURE.md                           |  12 +
 docs/M33fullaudit.md                              | 449 ++++++++++++
 docs/RefactorEnhancements.md                      | 364 ----------
 docs/certification/README.md                      |  31 +
 docs/ezra.md                                      |  20 +-
 docs/ezra_operating_manual_v1.md                  | 829 ++++++++++++++++++++++
 docs/milestones/M33/M33_audit.md                  | 182 +++++
 docs/milestones/M33/M33_run2.md                   | 170 +++++
 docs/milestones/M33/M33_summary.md                | 144 ++++
 docs/milestones/M33/M33_toolcalls.md              |   2 +
 docs/milestones/M34/M34_plan.md                   |  41 ++
 docs/milestones/M34/M34_toolcalls.md              |   6 +
 docs/milestones/M35/M35_audit.md                  |  53 ++
 docs/milestones/M35/M35_plan.md                   | 151 ++++
 docs/milestones/M35/M35_run1.md                   | 164 +++++
 docs/milestones/M35/M35_run2.md                   |  77 ++
 docs/milestones/M35/M35_summary.md                |  84 +++
 docs/milestones/M35/M35_toolcalls.md              |  22 +
 docs/milestones/M36/M36_plan.md                   |  21 +
 docs/milestones/M36/M36_toolcalls.md              |   5 +
 docs/prompts/RefactorMilestoneAuditPrompt.md      | 562 ---------------
 docs/prompts/RefactorSummaryPrompt.md             | 436 -----------
 docs/prompts/RefactorWorkflowPrompt.md            | 319 ---------
 docs/prompts/other/CodebaseAuditPromptV2.md         | 335 ---------
 docs/prompts/other/InitialRefactorAuditPrompt.md  | 272 -------
 docs/prompts/other/capabilitiesprompt.md          | 163 -----
 docs/prompts/other/novelanalysisprompt.md         | 136 ----
 docs/prompts/other/summaryprompt.md               | 252 -------
 docs/prompts/other/unifiedmilestoneauditprompt.md | 512 -------------
 docs/prompts/other/workflowprompt.md              | 292 --------
 docs/release/DISTRIBUTION_VERIFICATION.md         |  78 ++
 scripts/verify_distribution.py                    | 369 ++++++++++
 tests/test_distribution_verification.py           | 139 ++++
 tests/test_public_surface_freeze.py               |  18 +-
 40 files changed, 3195 insertions(+), 3866 deletions(-)
```

### `git diff --name-only 23789314ba5f6a502c650f6a098f12eb4ed0e8b4..HEAD`

```text
.cursorrules
.github/workflows/ci.yml
.github/workflows/release.yml
.gitignore
.pre-commit-config.yaml
README.md
docs/CI_ARCHITECTURE.md
docs/M33fullaudit.md
docs/RefactorEnhancements.md
docs/certification/README.md
docs/ezra.md
docs/ezra_operating_manual_v1.md
docs/milestones/M33/M33_audit.md
docs/milestones/M33/M33_run2.md
docs/milestones/M33/M33_summary.md
docs/milestones/M33/M33_toolcalls.md
docs/milestones/M34/M34_plan.md
docs/milestones/M34/M34_toolcalls.md
docs/milestones/M35/M35_audit.md
docs/milestones/M35/M35_plan.md
docs/milestones/M35/M35_run1.md
docs/milestones/M35/M35_run2.md
docs/milestones/M35/M35_summary.md
docs/milestones/M35/M35_toolcalls.md
docs/milestones/M36/M36_plan.md
docs/milestones/M36/M36_toolcalls.md
docs/prompts/RefactorMilestoneAuditPrompt.md
docs/prompts/RefactorSummaryPrompt.md
docs/prompts/RefactorWorkflowPrompt.md
docs/prompts/other/CodebaseAuditPromptV2.md
docs/prompts/other/InitialRefactorAuditPrompt.md
docs/prompts/other/capabilitiesprompt.md
docs/prompts/other/novelanalysisprompt.md
docs/prompts/other/summaryprompt.md
docs/prompts/other/unifiedmilestoneauditprompt.md
docs/prompts/other/workflowprompt.md
docs/release/DISTRIBUTION_VERIFICATION.md
scripts/verify_distribution.py
tests/test_distribution_verification.py
tests/test_public_surface_freeze.py
```

---

## 3. Local quality verification

**Platform:** Windows (PowerShell), Python 3.11.9

| Command | Result |
| --- | --- |
| `ruff check .` | ✅ All checks passed |
| `ruff format --check .` | ✅ 88 files already formatted |
| `mypy src` | ❌ **Failed** (3 errors; see below) |
| `pytest` | ✅ **267 passed**, 28 skipped in 2.76s |

### Mypy output (failure)

```text
src\ezra\zones\serialize.py:94: error: Unused "type: ignore" comment  [unused-ignore]
src\ezra\epb\schema_validator.py:16: error: Unused "type: ignore" comment  [unused-ignore]
src\ezra\tools\capture_easyocr_baseline.py:197: error: Incompatible types in assignment (expression has type "str", variable has type "TorchVersion")  [assignment]
Found 3 errors in 3 files (checked 40 source files)
```

**M36 note:** M36 introduced **no** `src/` changes. This local mypy failure is **orthogonal** to M36 closure evidence-only work; confirm on Linux CI / clean venv if investigating.

---

## 4. M36 file-change expectation

At completion of M36 **implementation commit**, changed paths should be limited to:

- `REFACTOR.md`
- `docs/release/AUDIT_RECONCILIATION_M33_M35.md`
- `docs/milestones/M36/*` (plan, run1, summary, audit, toolcalls)
- `docs/milestones/M37/*` (stubs)
- `docs/ezra.md` (optional governance row for M36)

**No** changes to `src/ezra/**`, `docs/specs/epb_v1/**`, `.github/workflows/**`, `pyproject.toml`, `requirements.txt`, `.gitignore`.

**Git note:** `.gitignore` contains `docs/milestones/` (local governance historic rule). Files under that path that are **already tracked** continue to update normally; **new** paths require `git add -f` to stage. M36 used `git add -f` for first-time tracked `M36_run1.md`, `M36_summary.md`, `M36_audit.md`, `M37_plan.md`, and `M37_toolcalls.md`.

---

## 5. Verdict (run log)

Repository inventory and reconciliation artifacts recorded; proceed to governance closeout (`M36_summary.md`, `M36_audit.md`).
