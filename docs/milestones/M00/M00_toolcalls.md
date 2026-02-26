# M00 Tool Calls Log

This document tracks all tool invocations during M00 milestone execution.

## Format

Each entry includes:
- Timestamp
- Tool name
- Purpose
- Files/targets involved
- Status (pending/completed/failed)

---

## Entries

### 2025-01-XX - Milestone Structure Creation
- **Tool:** `write`
- **Purpose:** Create milestone documentation structure (M00_plan.md, M00_toolcalls.md)
- **Files:** `docs/milestones/M00/M00_plan.md`, `docs/milestones/M00/M00_toolcalls.md`
- **Status:** ✅ Completed

### 2025-01-XX - M00 Implementation Complete
- **Tool:** Multiple (write, run_terminal_cmd)
- **Purpose:** Complete M00 genesis baseline implementation
- **Files:** All M00 deliverables (package skeleton, CI, tests, docs)
- **Status:** ✅ Completed
- **Notes:** 
  - Branch `m00-genesis-baseline` pushed to origin
  - PR #1 created: https://github.com/m-cahill/ezra/pull/1
  - Coverage: 100% (exceeds 85% requirement)
  - All tests passing locally

### 2026-02-26 - CI Workflow Analysis (M00_run1.md)
- **Tool:** `write`, `run_terminal_cmd` (gh CLI)
- **Purpose:** Generate CI workflow analysis per RefactorWorkflowPrompt.md
- **Files:** `docs/milestones/M00/M00_run1.md`
- **Status:** ✅ Completed
- **Notes:**
  - CI Run ID: 22422255082
  - Status: ❌ Failed (formatting violations)
  - Issue: 8 files need `ruff format` applied
  - All functional checks passed (lint, typecheck, tests, coverage)
  - Next: Fix formatting and re-run CI

### 2026-02-26 - Fix Formatting Violations
- **Tool:** `run_terminal_cmd` (ruff format)
- **Purpose:** Apply Ruff formatting to 8 files that failed format check
- **Files:** All Python files in `src/` and `tests/`
- **Status:** ✅ Completed
- **Notes:**
  - Applied `ruff format .` to fix all formatting violations
  - Committed and pushed to trigger CI re-run
  - Waiting for CI to complete

### 2026-02-26 - CI Workflow Analysis (M00_run2.md)
- **Tool:** `write`, `run_terminal_cmd` (gh CLI)
- **Purpose:** Generate CI workflow analysis for Run 2 per RefactorWorkflowPrompt.md
- **Files:** `docs/milestones/M00/M00_run2.md`
- **Status:** ✅ Completed
- **Notes:**
  - CI Run ID: 22422346345
  - Status: ❌ Failed (1 file still needs formatting)
  - Issue: `tests/test_smoke.py` needs reformatting
  - Ruff lint auto-fixed 19 errors (improvement)
  - All functional checks passed (typecheck, tests, coverage)
  - Next: Fix remaining formatting violation

### 2026-02-26 - Fix Remaining Formatting Violation
- **Tool:** `run_terminal_cmd` (ruff format)
- **Purpose:** Format `tests/test_smoke.py` that failed in Run 2
- **Files:** `tests/test_smoke.py`
- **Status:** ✅ Completed
- **Notes:**
  - Applied `ruff format tests/test_smoke.py`
  - Committed and pushed to trigger CI re-run
  - Waiting for CI to complete

