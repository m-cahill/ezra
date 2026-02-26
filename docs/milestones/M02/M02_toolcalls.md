# M02 Tool Calls Log

This document tracks all tool invocations during M02 milestone execution.

## Format

Each entry includes:
- Timestamp
- Tool name
- Purpose
- Files/targets involved
- Status (pending/completed/failed)

---

## Entries

### 2025-01-27 - Milestone Structure Creation
- **Tool:** `write`
- **Purpose:** Create M02 milestone documentation structure (M02_plan.md, M02_toolcalls.md)
- **Files:** `docs/milestones/M02/M02_plan.md`, `docs/milestones/M02/M02_toolcalls.md`
- **Status:** ✅ Completed

### 2025-01-27 - Branch Creation
- **Tool:** `run_terminal_cmd` (git)
- **Purpose:** Create working branch for M02
- **Files:** N/A
- **Status:** ✅ Completed
- **Notes:** Branch `m02-golden-parity-lock` created

### 2025-01-27 - Parity Module Implementation
- **Tool:** `write`
- **Purpose:** Create parity verification module with all required functions
- **Files:** `src/ezra/baseline/parity.py`
- **Status:** ✅ Completed
- **Notes:** Functions: load_baseline, load_manifest, validate_manifest_environment, compare_outputs, compute_file_sha256

### 2025-01-27 - Parity Tests Implementation
- **Tool:** `write`
- **Purpose:** Create integration parity tests (requires EZRA_RUN_PARITY=1)
- **Files:** `tests/test_parity.py`
- **Status:** ✅ Completed
- **Notes:** 4 integration tests: parity match, manifest match, canonicalization stability, baseline hash

### 2025-01-27 - Parity Unit Tests Implementation
- **Tool:** `write`
- **Purpose:** Create unit tests for parity utilities (no EasyOCR required)
- **Files:** `tests/test_parity_unit.py`
- **Status:** ✅ Completed
- **Notes:** 10 unit tests covering all pure functions

### 2025-01-27 - Pytest Parity Marker
- **Tool:** `search_replace` (pyproject.toml)
- **Purpose:** Add parity marker to pytest config
- **Files:** `pyproject.toml`
- **Status:** ✅ Completed

### 2025-01-27 - Baseline Hash Computation
- **Tool:** `run_terminal_cmd` (python)
- **Purpose:** Compute SHA256 hash of committed baseline.json
- **Files:** `tests/test_parity.py`
- **Status:** ✅ Completed
- **Notes:** Hash: 3157ebb21c5382221a22acaed154611172122ef6aab188b0bf15e02a5a018e60

### 2025-01-27 - Documentation Update
- **Tool:** `search_replace` (docs/ezra.md)
- **Purpose:** Add Golden Parity Discipline section and update milestone table
- **Files:** `docs/ezra.md`
- **Status:** ✅ Completed

### 2025-01-27 - Linting Fixes
- **Tool:** `search_replace` (parity.py)
- **Purpose:** Fix linting errors (unused import, line length)
- **Files:** `src/ezra/baseline/parity.py`
- **Status:** ✅ Completed

### 2025-01-27 - Formatting
- **Tool:** `run_terminal_cmd` (ruff format)
- **Purpose:** Apply code formatting
- **Files:** `src/ezra/baseline/parity.py`, `tests/test_parity.py`
- **Status:** ✅ Completed

### 2025-01-27 - Type Checking Fixes
- **Tool:** `search_replace` (parity.py)
- **Purpose:** Fix mypy type errors (type ignores for optional deps, json.load return type)
- **Files:** `src/ezra/baseline/parity.py`
- **Status:** ✅ Completed

### 2025-01-27 - CI Verification
- **Tool:** `run_terminal_cmd` (ruff, mypy, pytest)
- **Purpose:** Run full local CI checks
- **Files:** All
- **Status:** ✅ Completed
- **Notes:** 
  - Lint: ✅ Pass
  - Format: ✅ Pass
  - Type check: ✅ Pass (1 pre-existing error in capture_easyocr_baseline.py from M01)
  - Tests: ✅ Pass (36 passed, 4 skipped)
  - Coverage: ✅ 90.99% (above 85% threshold)

