# 📌 M04 Plan — Multi-Plugin Abstraction Layer

**Milestone ID:** M04
**Mode:** Behavior-Preserving Structural Extension
**Baseline:** `v0.0.4-m03`
**Branch:** `m04-multi-plugin-abstraction`

---

# 1. Intent / Target

Introduce a **plugin registry and plugin resolution layer** so EZRA can support:

* Multiple OCR backends (EasyOCR is just the first)
* Runtime plugin selection
* Clean separation between:

  * Plugin interface
  * Plugin implementation
  * Plugin discovery

After M04:

* `EasyOCRPlugin` becomes a registered plugin.
* EZRA can resolve plugins by name.
* Core remains ML-free.
* No behavior change to existing EasyOCR usage.
* Parity still passes unchanged.

---

# 2. Scope Boundaries

## In Scope

1. Introduce plugin registry system:

   * `src/ezra/plugins/registry.py`
   * Static registry mapping plugin names → plugin classes

2. Add factory function:

   ```python
   get_plugin(name: str, **kwargs) -> OCRPlugin
   ```

3. Refactor current EasyOCR usage path to use registry internally (without changing public API)

4. Add unit tests for:

   * Registry resolution
   * Unknown plugin error
   * Plugin class lookup
   * Instantiation correctness

5. Update documentation in `docs/ezra.md` to describe:

   * Plugin registration policy
   * Naming conventions
   * Extension pattern

6. Ensure parity suite passes unchanged.

---

## Out of Scope

* New OCR backends
* Entry-point based dynamic loading
* CVAT integration
* Plugin auto-discovery via packaging metadata
* Runtime configuration systems
* CLI interface changes

---

# 3. Invariants (Must Not Change)

From `docs/ezra.md` :

* CI must remain truthful.
* Plugin-first posture maintained.
* Core remains ML-free.
* Parity gate must pass unchanged.
* No baseline updates.
* Coverage ≥85%.

Additional M04 invariant:

> Registry introduction must not alter EasyOCR behavior or initialization semantics.

---

# 4. Architectural Design

## New Module

### `src/ezra/plugins/registry.py`

```python
from typing import Type, Dict
from .interface import OCRPlugin
from .easyocr_plugin import EasyOCRPlugin

_PLUGIN_REGISTRY: Dict[str, Type[OCRPlugin]] = {
    "easyocr": EasyOCRPlugin,
}
```

### Public Factory

```python
def get_plugin(name: str, **kwargs) -> OCRPlugin:
    try:
        plugin_cls = _PLUGIN_REGISTRY[name]
    except KeyError:
        raise ValueError(f"Unknown plugin: {name}")
    return plugin_cls(**kwargs)
```

---

## Why Static Registry (for now)?

Because:

* Deterministic
* Simple
* No packaging complexity
* No dynamic import risks
* Fully testable

Dynamic plugin discovery can be M06+.

---

# 5. Implementation Steps (Ordered & Reversible)

1. Create `registry.py`.
2. Register `EasyOCRPlugin`.
3. Add `get_plugin()` factory.
4. Add registry unit tests.
5. Ensure no direct behavior path changes.
6. Run full local checks.
7. Run parity suite.
8. Open PR.
9. Generate `M04_run1.md`.

Rollback plan: revert PR — no migrations involved.

---

# 6. Verification Plan

Before PR:

```
ruff check .
ruff format --check .
mypy src
pytest
EZRA_RUN_PARITY=1 pytest -m parity
```

Must observe:

* All unit tests pass
* Parity passes unchanged
* Coverage ≥85%

---

# 7. Risk & Blast Radius

| Risk                   | Mitigation                     |
| ---------------------- | ------------------------------ |
| Plugin resolution typo | Registry tests                 |
| Behavior drift         | Parity suite                   |
| Interface misbinding   | Type checking + ABC compliance |
| Silent behavior change | No code path rewrites          |

Blast radius: low. No core modifications.

---

# 8. Deliverables

Code:

* `registry.py`
* Updated imports if necessary

Tests:

* `test_plugin_registry.py`

Docs:

* Update `docs/ezra.md` milestone table
* Add short section: "Plugin Registration Policy"

Milestone fold:

* `M04_plan.md`
* `M04_toolcalls.md`
* `M04_run1.md`
* `M04_summary.md`
* `M04_audit.md`

Tag after merge:

```
v0.0.5-m04
```

---

# 9. Acceptance Criteria

M04 is complete when:

* Registry exists
* EasyOCR registered
* Factory tested
* No behavior drift
* Parity unchanged
* CI green
* Coverage ≥85%
* Documentation updated
* Milestone artifacts generated

---

# 10. Strategic Outcome

After M04, EZRA transitions from:

> Single-plugin architecture

to

> Plugin-capable perception substrate.

This unlocks:

* Tesseract backend (future)
* Custom CV models
* Synthetic test plugins
* Experimental research adapters

Without touching core again.

