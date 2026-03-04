# M00 Run 3 — CI Workflow Analysis

**Generated:** 2026-02-26  
**Workflow Run:** [22424737964](https://github.com/m-cahill/ezra/actions/runs/22424737964)  
**PR:** [#1](https://github.com/m-cahill/ezra/pull/1)  
**Analysis Format:** `docs/prompts/RefactorWorkflowPrompt.md`

---

## 1. Workflow Identity

| Field | Value |
|-------|-------|
| **Workflow Name** | CI |
| **Run ID** | 22424737964 |
| **Trigger** | Pull Request (#1) — push after pipeline fix |
| **Branch** | `m00-genesis-baseline` |
| **Commit SHA** | `d17d725` |
| **PR Number** | 1 |
| **Status** | ✅ **Success** |
| **Conclusion** | success |
| **Created** | 2026-02-26T02:07:16Z |
| **URL** | https://github.com/m-cahill/ezra/actions/runs/22424737964 |

---

## 2. Change Context (Refactor-Specific)

| Field | Value |
|-------|-------|
| **Milestone** | M00 — Genesis Baseline |
| **Phase** | CI Monitoring & Analysis (Phase 4) |
| **Declared Intent** | Fix CI pipeline ordering bug; apply lint fixes; add LF normalization |
| **Refactor Target Surface** | CI workflow, type annotations, unused imports |
| **Milestone Posture** | **Behavior-Preserving** (no logic changes, only lint + CI config) |
| **Run Type** | Corrective (fixing Run 1 & Run 2 failures) |

**Baseline Reference:**
- **Last Known Green:** None (this is genesis baseline — first green)
- **Previous Runs:**
  - [22422255082](https://github.com/m-cahill/ezra/actions/runs/22422255082) — Run 1: ❌ Failed (8 files needed formatting)
  - [22422346345](https://github.com/m-cahill/ezra/actions/runs/22422346345) — Run 2: ❌ Failed (1 file still needed formatting)
  - [22424402274](https://github.com/m-cahill/ezra/actions/runs/22424402274) — Run 2.5: ❌ Failed (same issue, `.gitattributes` added but root cause was elsewhere)
- **Declared Invariants:**
  - Repository remains buildable
  - No hidden runtime behavior introduced
  - CI must be truthful (no `continue-on-error`, no skipped required checks)
  - Coverage measured from day one (≥85%)
  - No EasyOCR code included
  - No CVAT code included

---

## 3. Workflow Inventory

| Job / Check | Required? | Purpose | Pass/Fail | Notes |
|------------|-----------|---------|-----------|-------|
| **Lint** | ✅ Yes | Ruff lint + format check | ✅ **PASS** | All checks clean |
| └─ Ruff (lint) | ✅ Yes | Static analysis (`--no-fix`) | ✅ Pass | "All checks passed!" — 0 errors |
| └─ Ruff (format check) | ✅ Yes | Formatting consistency | ✅ Pass | "8 files already formatted" |
| **Type Check** | ✅ Yes | Mypy static type checking | ✅ **PASS** | "Success: no issues found in 6 source files" |
| **Test** | ✅ Yes | Pytest + Coverage | ✅ **PASS** | 3/3 tests passed, 100% coverage |
| └─ Pytest with coverage | ✅ Yes | Run tests + collect coverage | ✅ Pass | 3 passed in 0.06s |
| └─ Coverage report | ✅ Yes | Enforce ≥85% gate | ✅ Pass | 100.00% (36 stmts, 0 miss) |
| └─ Upload coverage XML | ✅ Yes | Artifact preservation | ✅ Pass | Artifact ID 5665155809 |
| └─ CI Summary | ℹ️ Info | Summary to PR | ✅ Pass | Coverage report written to step summary |

**Governance checks:**
- ❌ No `continue-on-error` anywhere
- ❌ No skipped required checks
- ❌ No muted or weakened gates
- ❌ No new, removed, or reclassified checks vs previous runs
- ✅ CI to use `--no-fix` prevents file mutation during checks (new guardrail)

---

## 4. Refactor Signal Integrity

### A) Tests

| Tier | Present? | Result |
|------|----------|--------|
| Smoke | ✅ | 3/3 passed |
| Unit | N/A | Not applicable for M00 (no logic) |
| Integration | N/A | Not applicable |
| Contract | N/A | Not applicable |
| E2E | N/A | Not applicable |

Tests cover the full refactor target surface:
- `test_import_ezra`: Import stability for all package modules
- `test_engine_instantiation`: Engine + plugin wiring
- `test_plugin_interface`: ABC interface contract

No golden/snapshot tests needed (M00 has no behavior to snapshot).
No missing tests for the touched surface.

### B) Coverage

| Metric | Value |
|--------|-------|
| Line coverage | 100.00% |
| Branch coverage | 100.00% (0 branches missed) |
| Gate | ≥85% — **EXCEEDED** |
| Statements | 36 total, 0 missed |

| File | Stmts | Miss | Branch | BrPart | Cover |
|------|-------|------|--------|--------|-------|
| `src/ezra/core/engine.py` | 4 | 0 | 0 | 0 | 100.00% |
| `src/ezra/plugins/interface.py` | 9 | 0 | 0 | 0 | 100.00% |
| `src/ezra/types.py` | 23 | 0 | 0 | 0 | 100.00% |

No exclusions expanded. Coverage is scoped correctly to `src/`.
Coverage is meaningful for M00: it verifies all type definitions, plugin interface, and engine skeleton are importable and instantiable.

### C) Static / Policy Gates

| Gate | Tool | Version | Result |
|------|------|---------|--------|
| Lint | Ruff | 0.15.2 | ✅ All checks passed |
| Format | Ruff | 0.15.2 | ✅ 8 files already formatted |
| Type check | Mypy | 1.19.1 | ✅ No issues in 6 source files |

No import boundary breaks, circular deps, or layering violations detected.
CI now uses `--no-fix` to prevent `ruff check` from mutating files during checks.

### D) Security / Supply Chain Signals

Not present in M00 scope (deferred to hardening milestone per locked decisions).

### E) Performance / Benchmarks

Not applicable for M00 (no runtime logic).

---

## 5. Root Cause Analysis — Previous Failures (Runs 1–2.5)

### The Bug

The CI pipeline had an ordering/configuration bug that caused persistent format check failures across 3 consecutive runs:

1. **`pyproject.toml`** contained `fix = true` under `[tool.ruff]`
2. **CI step** ran `ruff check .` which — due to `fix = true` — **auto-fixed 19 lint errors and wrote changes to disk**
3. **Next CI step** ran `ruff format --check .` which found the **modified-but-unformatted** files

The 19 auto-fixes were legitimate lint improvements:
- `UP035`: Replace `typing.Dict`/`typing.List` with `dict`/`list` (PEP 585)
- `UP007`: Replace `Optional[X]` with `X | None` (PEP 604)
- `F401`: Remove unused imports (`Mock`, `pytest` in `test_smoke.py`)

After lint-fixing `test_smoke.py` (removing 4 lines of unused imports), the file needed reformatting (blank line consolidation), which produced the persistent "1 file would be reformatted" signal.

### The Fix

1. Applied `ruff check --fix .` locally (19 fixes applied)
2. Applied `ruff format .` locally (1 file reformatted after lint fixes)
3. Changed CI to `ruff check --no-fix .` — CI must never mutate files during checks
4. Added `.gitattributes` with `* text=auto eol=lf` for cross-platform determinism

### Why Initial Diagnosis Was Wrong

The initial diagnosis (CRLF/LF drift) was a reasonable hypothesis given:
- Windows development environment with `core.autocrlf=true`
- CRLF warnings during git operations
- Single file consistently failing format check

However, investigation confirmed `core.autocrlf=true` was already normalizing blobs to LF. The real root cause was the CI pipeline itself mutating files between check steps.

### Lessons

1. **CI must never modify files during checks** — `--no-fix` / `--check` flags are mandatory
2. **`fix = true` in config is dangerous for CI** — it silently converts `check` commands into `fix` commands
3. **Persistent CI failures require looking at the pipeline itself**, not just the files it reports

---

## 6. Delta Analysis (Change Impact vs Baseline)

### Change Inventory (Run 3 vs Run 2)

| File | Change | Category |
|------|--------|----------|
| `.github/workflows/ci.yml` | `ruff check .` → `ruff check --no-fix .` | CI guardrail |
| `.gitattributes` | New file: `* text=auto eol=lf` | Environment determinism |
| `src/ezra/types.py` | `Dict`→`dict`, `List`→`list`, `Optional[X]`→`X \| None` | Lint fix (UP035/UP007) |
| `src/ezra/plugins/interface.py` | `Dict`→`dict`, removed unused `Dict` import | Lint fix (UP035) |
| `tests/test_smoke.py` | Removed unused `Mock`, `pytest` imports | Lint fix (F401) |
| `docs/milestones/M00/M00_toolcalls.md` | Updated with root cause analysis | Governance |

### Expected vs Observed

- **Expected:** All 3 jobs pass after applying lint fixes and adding `--no-fix`
- **Observed:** ✅ All 3 jobs passed. Exact match.

### Refactor-Specific Drift Detection

- **Signal drift:** None. No tests skipped, no coverage misleading, no gates bypassed.
- **Coupling revealed:** None. Changes were isolated to lint/formatting concerns.
- **Hidden dependencies:** None exposed.

---

## 7. Invariants & Guardrails Check

| Invariant | Status | Evidence |
|-----------|--------|----------|
| Repository remains buildable | ✅ Held | CI green, all jobs passed |
| No hidden runtime behavior introduced | ✅ Held | Only stub modules, type annotation modernization |
| CI must be truthful | ✅ Held | No `continue-on-error`, no skipped checks, `--no-fix` guardrail added |
| Coverage measured from day one | ✅ Held | 100% coverage, ≥85% gate enforced |
| No EasyOCR code included | ✅ Held | No EasyOCR imports in codebase |
| No CVAT code included | ✅ Held | No CVAT references in codebase |

**No invariants violated.**

**New guardrail established:** CI now uses `--no-fix` for `ruff check`, preventing silent file mutation during CI checks.

---

## 8. Verdict

> **Verdict:** CI is truthfully green. All three quality gates (lint, typecheck, test+coverage) pass cleanly on Ubuntu 24.04 with Python 3.11.14, Ruff 0.15.2, Mypy 1.19.1, Pytest 9.0.2, and Coverage 7.13.4. The persistent format check failure across Runs 1–2.5 has been definitively resolved by identifying the root cause (CI pipeline mutating files via `fix = true` before format check) and applying a precise, minimal fix. The repository is now deterministic across Windows development and Linux CI environments. All M00 invariants hold. Coverage is 100%. No scope expansion beyond legitimate CI guardrail hardening.

**✅ Merge approved**

---

## 9. Next Actions

| # | Action | Owner | Scope | Milestone |
|---|--------|-------|-------|-----------|
| 1 | Obtain merge permission from user | Human | PR #1 | M00 |
| 2 | Generate M00_summary.md | Cursor | `docs/milestones/M00/` | M00 |
| 3 | Generate M00_audit.md | Cursor | `docs/milestones/M00/` | M00 |
| 4 | Update `docs/ezra.md` milestone table | Cursor | `docs/ezra.md` | M00 |
| 5 | Tag `v0.0.1.dev0` after merge | Human/Cursor | Repository | M00 |
| 6 | Begin M01 planning (EasyOCR Baseline Harness) | Human | New milestone | M01 |

---

## Appendix: CI Environment

| Component | Version |
|-----------|---------|
| Runner OS | Ubuntu 24.04.3 LTS |
| Runner Image | ubuntu-24.04 (20260224.36.1) |
| Python | 3.11.14 |
| Ruff | 0.15.2 |
| Mypy | 1.19.1 |
| Pytest | 9.0.2 |
| pytest-cov | 7.0.0 |
| Coverage | 7.13.4 |
| Git | 2.53.0 |

---

## Run History

| Run | ID | Status | Root Cause |
|-----|----|--------|------------|
| Run 1 | 22422255082 | ❌ Failed | 8 files needed `ruff format` (initial formatting not applied) |
| Run 2 | 22422346345 | ❌ Failed | 1 file still needed formatting (lint auto-fix + format interaction) |
| Run 2.5 | 22424402274 | ❌ Failed | `.gitattributes` added but root cause was pipeline ordering, not line endings |
| **Run 3** | **22424737964** | **✅ Success** | **Root cause fixed: lint fixes applied locally, CI uses `--no-fix`** |



