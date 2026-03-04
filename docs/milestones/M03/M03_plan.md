# 🚧 M03 — Structural Extraction of EasyOCR Integration

**Mode:** Behavior-Preserving Structural Refactor
**Posture:** Preserve (Parity-Enforced)
**Baseline:** `v0.0.3-m02`
**Branch:** `m03-structural-extraction-easyocr`

---

# 1. Objective

Refactor `EasyOCRPlugin` into a **cleanly layered integration boundary** while preserving exact behavior verified by the M02 parity gate.

After M03:

* EasyOCR-specific logic is isolated behind an adapter layer.
* Plugin interface remains stable.
* Core runtime remains ML-free.
* Parity suite proves no behavioral drift.

---

# 2. Why M03 Exists

From M02 audit :

> Parity gate provides refactor safety substrate required for structural extraction work.

From ezra.md :

> Plugin-first posture: core engine remains ML-free; ML is loaded via plugin interfaces.

Right now:

* `EasyOCRPlugin` directly instantiates and manages `easyocr.Reader`
* EasyOCR model orchestration and transformation logic are embedded inside the plugin

This is fine for baseline capture — but not ideal for long-term extensibility.

M03 prepares EZRA for:

* Multiple OCR backends
* Swappable inference adapters
* Cleaner testability
* Future CVAT-export compatibility

---

# 3. Refactor Target

Current structure (conceptual):

```
EasyOCRPlugin
 ├── easyocr.Reader(...)
 ├── raw inference
 ├── bbox transformation
 └── output normalization
```

Target structure:

```
EasyOCRPlugin (implements OCRPlugin)
 └── EasyOCRAdapter
        ├── Reader lifecycle
        ├── Inference call
        └── Raw detection extraction

Transformation Layer (separate pure function)
 └── easyocr_to_ezra_format(...)
```

---

# 4. Scope

## In Scope

1. Create `src/ezra/plugins/easyocr_adapter.py`

   * Encapsulate all direct EasyOCR interaction
   * Responsible only for:

     * Model initialization
     * Inference call
     * Raw output extraction

2. Refactor `EasyOCRPlugin` to:

   * Use adapter
   * Remove direct Reader usage
   * Remain compliant with `OCRPlugin` ABC

3. Extract transformation logic into pure function:

   * `transform_easyocr_output(raw_output)`

4. Add adapter unit tests (mock-based)

5. Ensure parity suite passes without baseline update

6. Maintain coverage ≥85%

---

## Out of Scope

* Behavior changes
* Performance optimization
* New plugins
* Multi-model support
* CVAT integration
* Baseline modification

---

# 5. Architectural Rules

## Must Remain True

* Plugin interface unchanged
* Canonical output identical
* No ML code enters `core/`
* No CI weakening
* Parity must pass before merge

## New Structural Invariant

After M03:

> All third-party ML framework calls must be isolated in adapter modules, never in plugin orchestration layer.

---

# 6. Deliverables

### Code

```
src/ezra/plugins/easyocr_adapter.py
```

```
class EasyOCRAdapter:
    def __init__(...)
    def infer(...)
```

Refactor:

```
src/ezra/plugins/easyocr_plugin.py
```

Now:

```
plugin -> adapter -> transform -> return canonical detections
```

---

### Tests

Add:

```
tests/test_easyocr_adapter.py
```

Unit tests must:

* Mock easyocr.Reader
* Validate:

  * Reader instantiated correctly
  * infer() calls reader correctly
  * Output returned unchanged from adapter layer

Parity tests must:

* Still pass
* No baseline update required

---

# 7. Refactor Safety Protocol

Before PR:

```
pytest
ruff check .
mypy src
EZRA_RUN_PARITY=1 pytest -m parity
```

Parity must pass locally.

If parity fails:

* Abort refactor
* Diagnose structural drift

No baseline edits allowed in M03.

---

# 8. CI Requirements

Unchanged:

* Lint
* Format
* Type check
* Test
* Coverage ≥85%

Parity remains local-only.

---

# 9. Expected Size

* ~200–300 lines moved/refactored
* Minimal new logic
* Moderate test adjustments
* 1 milestone fold
* 1–2 CI cycles

---

# 10. Risk Profile

| Risk                             | Mitigation         |
| -------------------------------- | ------------------ |
| Subtle bbox transformation drift | Parity suite       |
| Reader lifecycle regression      | Adapter unit tests |
| Import boundary violation        | Mypy + CI          |
| Hidden dependency drift          | Manifest unchanged |

---

# 11. Acceptance Criteria

M03 is complete when:

* Adapter layer created
* Plugin uses adapter
* Transformation extracted to pure function
* Parity suite passes unchanged
* Coverage ≥85%
* CI green
* No baseline update
* Milestone fold created
* M03_summary + M03_audit generated

---

# 12. Cursor Execution Steps

1. Create branch `m03-structural-extraction-easyocr`
2. Extract adapter class
3. Refactor plugin
4. Extract transform function
5. Add adapter tests
6. Run full local checks
7. Run parity suite
8. Open PR
9. Generate `M03_run1.md`
10. Await merge permission

---

# 13. Strategic Context

M00 → CI discipline
M01 → Baseline capture
M02 → Parity enforcement
M03 → Structural decoupling

After M03:

EZRA will have:

* Clean integration boundaries
* Refactor safety
* Deterministic output discipline
* Plugin-ready architecture

At that point, you have a **production-grade perception substrate**.

