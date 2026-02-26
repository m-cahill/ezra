# M00_plan — EZRA Genesis Baseline

## 1. Intent / Target

Establish the **foundational governance, structure, and CI baseline** for EZRA while preserving the current repository behavior (which is effectively empty except for `LICENSE`).

M00 is a **non-functional milestone**:

* No OCR logic.
* No EasyOCR import.
* No CVAT integration.
* No training code.
* No model execution.

The goal is to:

* Lock architectural boundaries.
* Introduce a minimal package skeleton.
* Establish truthful CI.
* Create milestone discipline from day one.

This is a **Genesis Baseline**.

---

## 2. Scope Boundaries (Strict)

### In Scope

* Repository structure
* Documentation scaffold
* Minimal Python package skeleton
* Plugin interface contract (no implementation)
* CI pipeline (lint + typecheck + tests + coverage gate)
* Milestone documentation fold for M00

### Explicitly Out of Scope

* EasyOCR import or refactor
* CVAT integration
* Model training
* Model execution
* Artifact hashing
* Feature graph
* Any performance changes
* Any behavior change (there is no behavior yet)

---

## 3. Invariants

Since the repo only contains `LICENSE`, our invariants are structural:

| Invariant                             | Verification                                       |
| ------------------------------------- | -------------------------------------------------- |
| Repository remains buildable          | CI green                                           |
| No hidden runtime behavior introduced | Only stub modules                                  |
| CI must be truthful                   | No `continue-on-error`, no skipped required checks |
| Coverage measured from day one        | Coverage gate enforced                             |
| No EasyOCR code included              | Repo search check                                  |
| No CVAT code included                 | Repo search check                                  |

---

## 4. Deliverable Structure

After M00, the repository must contain:

```
ezra/
├── LICENSE
├── README.md
├── .gitignore
├── pyproject.toml
├── src/
│   └── ezra/
│       ├── __init__.py
│       ├── core/
│       │   └── engine.py
│       ├── plugins/
│       │   └── interface.py
│       └── types.py
├── tests/
│   └── test_smoke.py
├── docs/
│   ├── VISION.md
│   ├── ezra.md
│   └── milestones/
│       └── M00/
│           ├── M00_plan.md
│           ├── M00_run1.md
│           ├── M00_summary.md
│           ├── M00_audit.md
│           └── M00_toolcalls.md
└── .github/workflows/ci.yml
```

---

## 5. Implementation Steps (Ordered + Reversible)

### Step 1 — Add Vision Document

Add:

* `docs/VISION.md`

This document defines:

* EZRA as runtime inference engine
* RediAI-v3 as training system
* CVAT as upstream annotation system
* Clear separation of concerns

No references to implementation yet.

**Status:** ✅ Already present — treat as complete.

---

### Step 2 — Create Minimal Python Package Skeleton

Add `pyproject.toml`:

* Python ≥ 3.11
* Ruff
* Mypy
* Pytest
* Coverage
* No runtime dependencies

Create minimal modules:

### `src/ezra/types.py`

Define:

* `ImageInput`
* `OCRResult`
* `ModelArtifactMetadata`

Pure dataclasses or TypedDicts.
No logic.

### `src/ezra/plugins/interface.py`

Define abstract base class:

```python
from abc import ABC, abstractmethod

class OCRPlugin(ABC):
    @abstractmethod
    def load(self, artifact_path: str) -> None:
        ...

    @abstractmethod
    def infer(self, image) -> dict:
        ...

    @abstractmethod
    def describe_capabilities(self) -> dict:
        ...
```

No implementation.

### `src/ezra/core/engine.py`

Add minimal placeholder:

```python
class EzraEngine:
    def __init__(self, plugin):
        self.plugin = plugin
```

No inference logic.

---

### Step 3 — Add Smoke Test

`tests/test_smoke.py`

Tests:

* Import ezra
* Instantiate engine with mock plugin
* Assert no crash

This locks import stability.

---

### Step 4 — Add Truthful CI

Create `.github/workflows/ci.yml`

Required jobs:

* Lint (ruff)
* Typecheck (mypy)
* Test (pytest + coverage)

Coverage gate:

* Set to **85% minimum**
* No `continue-on-error`
* All jobs required

Important:

* CI must fail if coverage drops.
* CI must fail on lint/type errors.

---

### Step 5 — Create Milestone Fold

Create:

```
docs/milestones/M00/
```

Include:

* M00_plan.md (this file)
* Placeholder M00_summary.md
* Placeholder M00_audit.md
* M00_toolcalls.md (initial empty log)
* M00_run1.md (to be generated after CI run)

---

### Step 6 — Commit Strategy

Branch name:

```
m00-genesis-baseline
```

Single cohesive PR.

No extra commits after merge.

---

## 6. Verification Plan

After PR is opened:

1. CI run must pass.
2. Coverage ≥ 85%.
3. Ruff clean.
4. Mypy clean.
5. No unexpected files.
6. Repo search confirms:

   * No EasyOCR imports.
   * No CVAT references.

Cursor must generate:

* M00_run1.md (CI analysis)
* M00_summary.md
* M00_audit.md

Only then can we merge.

---

## 7. Risk & Rollback Plan

Risk level: Extremely low (additive only).

Rollback:

* Revert PR.
* No data migrations.
* No runtime artifacts.

---

## 8. Exit Criteria

M00 is complete when:

* CI green.
* Coverage enforced.
* Milestone fold complete.
* Summary + audit generated.
* Merge to main.
* Tag created:

```
v0.0.1-m00
```

---

# Strategic Notes

M00 establishes:

* Governance discipline from day one.
* Clear separation from RediAI-v3.
* Clear boundary from CVAT.
* Plugin-first architecture.
* CI truthfulness as non-negotiable.

Only after M00 closes do we proceed to:

**M01 — EasyOCR Baseline Harness (Behavior Capture).**

