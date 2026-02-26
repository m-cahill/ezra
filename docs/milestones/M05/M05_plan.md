# 🟢 M05 Plan — Plugin Configuration & Interface Hardening

**Milestone ID:** M05
**Mode:** Structural Hardening
**Posture:** Behavior-Preserving
**Baseline Tag:** `v0.0.5-m04`
**Goal:** Make plugin resolution configurable and interface-contract-safe without touching core or golden outputs.

---

# 1️⃣ Milestone Objective

M04 introduced a static plugin registry with lazy resolution.

M05 makes that registry:

* **Configurable (runtime-driven)**
* **Interface-hardened (strict contract enforcement)**
* **Future-proofed (multi-plugin ready without core edits)**

Without M05, adding new OCR backends requires touching code manually and risks silent interface drift.

After M05:

* Plugins can be selected via configuration
* Interface compliance is runtime-validated
* Core remains ML-free
* Parity discipline remains intact

---

# 2️⃣ Scope Definition

## ✅ In Scope

### A. Runtime Plugin Selection

Introduce:

```python
get_plugin_from_config(config: dict) -> OCRPlugin
```

Allow configuration format:

```python
{
    "name": "easyocr",
    "kwargs": {
        "lang_list": ["en"],
        "gpu": False
    }
}
```

Behavior:

* Validates presence of `"name"`
* Validates plugin exists
* Validates kwargs are passed through unchanged
* Returns instantiated plugin

No environment variables.
No dynamic loading.
No entry points.
Still deterministic.

---

### B. Strict Interface Enforcement

Add runtime guard:

After instantiation:

* Verify object is instance of `OCRPlugin`
* Verify required methods exist
* Raise deterministic `TypeError` if contract violated

This prevents silent plugin mis-registration.

---

### C. Registry Validation Guard

Add:

```python
validate_registry() -> None
```

* Iterates over registry
* Confirms module path resolves
* Confirms class exists
* Confirms subclass of `OCRPlugin`
* Does NOT instantiate heavy models

Used only in tests.

---

### D. Registry Test Expansion

Add tests covering:

* Valid config resolution
* Missing name key
* Unknown plugin
* Malformed registry entry
* Non-subclass registration failure
* Invalid kwargs propagation

Target: 100% coverage of registry module maintained.

---

### E. Documentation Update

Update:

* `docs/ezra.md` — Add section "Plugin Configuration Format"
* Explicitly state:

  * Registry remains static
  * No dynamic discovery
  * Deterministic resolution only

---

## ❌ Out of Scope

* Entry-point discovery
* Auto-registration
* CLI exposure
* Environment variable resolution
* CVAT integration
* Training integration
* Multi-process model management
* Baseline update

---

# 3️⃣ Invariants (Must Not Break)

From `docs/ezra.md`:

* Core remains ML-free
* CI remains truthful
* Parity unchanged
* No network during PR gate
* Deterministic text normalization preserved

From M04:

* Behavior-preserving posture
* No golden baseline update
* No output schema changes

From M04:

* Registry pattern preserved
* Lazy import preserved
* Plugin interface unchanged

---

# 4️⃣ Files Expected to Change

Likely modifications:

```
src/ezra/plugins/registry.py
tests/test_plugin_registry.py
docs/ezra.md
docs/milestones/M05/*
```

No changes allowed in:

* `core/`
* `baseline/`
* Golden artifacts
* CI workflow

---

# 5️⃣ CI & Coverage Requirements

Hard Gates:

* Coverage ≥ 85% (currently 95.86%)
* Registry remains 100% covered
* mypy passes
* ruff passes
* pydocstyle passes
* No threshold lowering
* No continue-on-error

Parity tests:

* Must pass locally
* Must NOT require CI to run them

---

# 6️⃣ Acceptance Criteria (Definition of Done)

M05 is complete only if:

* `get_plugin_from_config()` implemented
* Runtime contract enforcement added
* Registry validation function exists
* All new tests pass
* Registry coverage remains 100%
* Overall coverage ≥ previous milestone
* No golden baseline change
* CI green on main
* No invariant regressions

---

# 7️⃣ Deliverables to Produce

Create:

```
docs/milestones/M05/M05_plan.md
docs/milestones/M05/M05_run1.md
docs/milestones/M05/M05_summary.md
docs/milestones/M05/M05_audit.md
docs/milestones/M05/M05_toolcalls.md
```

Follow existing artifact pattern from M04.

Tag on completion:

```
v0.0.6-m05
```

---

# 8️⃣ Risk Assessment

### Primary Risk

Accidental behavior drift via altered instantiation semantics.

Mitigation:

* Do not modify plugin constructor behavior.
* Do not modify canonicalization.
* Run parity suite before merge.

### Secondary Risk

Over-engineering registry.

Mitigation:

* Keep static mapping.
* No new dependency.
* No reflection-based auto discovery.

---

# 9️⃣ Exit Statement Template (For M05 Audit)

> M05 hardened plugin resolution through runtime configuration and strict interface validation while preserving all behavioral invariants. No output drift observed. CI gates maintained. Registry abstraction strengthened without expanding architectural surface.

---

# 🔟 After M05 (Future Direction — Not Part of This Milestone)

M06 candidates:

* Second OCR backend (Tesseract plugin)
* Entry-point discovery (optional)
* Plugin metadata introspection
* Config schema formalization

But M05 is purely structural hardening.

---

# Final Cursor Instruction

Proceed with:

```
M05 — Plugin Configuration & Interface Hardening
```

Behavior-preserving.
Invariant-respecting.
No golden updates.
No scope creep.

