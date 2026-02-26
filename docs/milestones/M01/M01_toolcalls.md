# M01 Tool Calls Log

This document tracks all tool invocations during M01 milestone execution.

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
- **Purpose:** Create M01 milestone documentation structure (M01_plan.md, M01_toolcalls.md)
- **Files:** `docs/milestones/M01/M01_plan.md`, `docs/milestones/M01/M01_toolcalls.md`
- **Status:** ✅ Completed

### 2025-01-27 - Branch Creation
- **Tool:** `run_terminal_cmd` (git)
- **Purpose:** Create working branch for M01
- **Files:** N/A
- **Status:** ✅ Completed
- **Notes:** Branch `m01-easyocr-baseline` created

### 2025-01-27 - Dependencies Added
- **Tool:** `search_replace` (pyproject.toml)
- **Purpose:** Add EasyOCR==1.7.2 as optional dependency and Pillow as dev dependency
- **Files:** `pyproject.toml`
- **Status:** ✅ Completed

### 2025-01-27 - EasyOCRPlugin Implementation
- **Tool:** `write`
- **Purpose:** Create EasyOCR plugin wrapper implementing OCRPlugin interface
- **Files:** `src/ezra/plugins/easyocr_plugin.py`
- **Status:** ✅ Completed
- **Notes:** Includes ImportError handling for optional dependency

### 2025-01-27 - Canonicalization Utility
- **Tool:** `write`
- **Purpose:** Create baseline canonicalization utilities (deterministic ordering/rounding)
- **Files:** `src/ezra/baseline/__init__.py`, `src/ezra/baseline/canonicalize.py`
- **Status:** ✅ Completed

### 2025-01-27 - Baseline Capture Tool
- **Tool:** `write`
- **Purpose:** Create baseline capture tool for golden output generation
- **Files:** `src/ezra/tools/__init__.py`, `src/ezra/tools/capture_easyocr_baseline.py`
- **Status:** ✅ Completed
- **Notes:** Generates fixtures at runtime via PIL, captures manifest with model checksums

### 2025-01-27 - Test Suite
- **Tool:** `write`
- **Purpose:** Add tests for plugin (mocked), canonicalization, and baseline schema validation
- **Files:** `tests/test_easyocr_plugin.py`, `tests/test_canonicalize.py`, `tests/test_baseline_schema.py`
- **Status:** ✅ Completed
- **Notes:** Plugin tests use mocking, baseline schema tests skip if baseline not captured

### 2025-01-27 - Pytest Integration Marker
- **Tool:** `search_replace` (pyproject.toml)
- **Purpose:** Add integration marker to pytest config
- **Files:** `pyproject.toml`
- **Status:** ✅ Completed

### 2025-01-27 - Documentation Update
- **Tool:** `search_replace` (docs/ezra.md)
- **Purpose:** Expand docs/ezra.md to source-of-truth format with all sections
- **Files:** `docs/ezra.md`
- **Status:** ✅ Completed

### 2025-01-27 - Linting Fixes
- **Tool:** `search_replace` (multiple files)
- **Purpose:** Fix linting errors (unused imports, line length, OSError aliases)
- **Files:** `src/ezra/plugins/easyocr_plugin.py`, `src/ezra/tools/capture_easyocr_baseline.py`, `tests/test_canonicalize.py`
- **Status:** ✅ Completed
- **Notes:** All linting checks pass

### 2025-01-27 - Test Fix
- **Tool:** `search_replace` (tests/test_canonicalize.py)
- **Purpose:** Fix rounding test expectation (40.999999 rounds to 41.0)
- **Files:** `tests/test_canonicalize.py`
- **Status:** ✅ Completed

### 2025-01-27 - Baseline Capture Execution
- **Tool:** `run_terminal_cmd` (pip, python -m), `search_replace` (capture tool fixes)
- **Purpose:** Install EasyOCR and run baseline capture tool to generate golden outputs
- **Files:** `docs/baselines/easyocr/1.7.2/synthetic_basic/baseline.json`, `docs/baselines/easyocr/1.7.2/synthetic_basic/manifest.json`, `src/ezra/tools/capture_easyocr_baseline.py`
- **Status:** ✅ Completed
- **Notes:** 
  - Fixed PIL Image to numpy array conversion for EasyOCR compatibility
  - Removed emoji characters for Windows console compatibility
  - Generated 4 detections in baseline.json
  - Captured 2 model file checksums in manifest.json

### 2026-02-26 - M01 Closure
- **Tool:** `run_terminal_cmd` (gh, git)
- **Purpose:** Merge PR #2, create tag v0.0.2-m01, verify main branch CI
- **Files:** N/A
- **Status:** ✅ Completed
- **Notes:**
  - PR #2 merged to main (merge commit: 92bb042)
  - Tag v0.0.2-m01 created and pushed
  - Main branch CI verified green (Run: 22426628285)
  - No diff between PR head and merge commit (no formatting drift)

