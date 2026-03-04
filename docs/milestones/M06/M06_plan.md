# M06_plan — Tesseract Plugin (Second OCR Backend)

## Milestone ID

**M06 — Tesseract Plugin (Provider Boundary Extension)**

## Phase

Plugin Architecture Hardening (OCR Surface Expansion)

## Refactor Posture

**Behavior-Preserving (Default)**

No externally observable behavior may change for existing consumers.

---

# 1. Intent / Target

Introduce a **second OCR backend plugin** (`tesseract`) into the existing static plugin registry without:

* changing default plugin resolution,
* altering `get_plugin("easyocr")` behavior,
* introducing dynamic discovery,
* introducing new runtime dependencies,
* or weakening CI.

This milestone proves that:

> The plugin registry supports multi-backend extension without coupling, dynamic discovery, or behavior drift.

This is a structural hardening step before orchestration (M07).

---

# 2. Scope Boundaries

## In Scope

* Add `TesseractPlugin` implementation
* Register it statically in registry
* Add deterministic tests
* Maintain 100% registry coverage
* Preserve parity tests from M04/M05
* No change to CLI/API surface
* No change to default plugin behavior

## Explicitly Out of Scope

* No engine orchestration layer
* No dynamic plugin discovery
* No environment auto-detection
* No actual Tesseract binary invocation
* No external dependency added
* No Docker changes
* No performance tuning
* No ML logic

---

# 3. Invariants (Must Not Change)

These are binding and must be verified.

### Invariant 1 — EasyOCR Behavior

`get_plugin("easyocr")` behaves exactly as in M05.

**Verification:**

* All 4 parity tests pass unchanged
* No baseline snapshot update
* No golden file change

---

### Invariant 2 — Registry Determinism

Registry remains:

* Static
* Deterministic
* No dynamic import scanning
* Lazy import preserved

**Verification:**

* Registry snapshot test unchanged except for expected new entry
* No `importlib` usage introduced
* No directory scanning

---

### Invariant 3 — Public API Stability

No breaking changes to:

* `get_plugin(name)`
* plugin base interface
* error behavior
* exception types

**Verification:**

* Existing API tests pass
* No signature changes
* mypy passes without changes to consumers

---

### Invariant 4 — CI Integrity

No required checks weakened.
No thresholds reduced.

**Verification:**

* CI jobs unchanged
* Coverage ≥ 85%
* Registry coverage remains 100%

---

# 4. Verification Plan

## Tests to Add

### A. Plugin Instantiation Test

* `get_plugin("tesseract")` returns correct plugin instance

### B. Deterministic Registry Snapshot

* Update registry snapshot to include `"tesseract"`
* Assert ordering is deterministic (easyocr first, tesseract second)

### C. No Cross-Plugin Coupling

* Ensure Tesseract import does not import EasyOCR module

### D. Error Surface

* Unknown plugin still raises same error type

---

## CI Evidence Required

* Lint: pass
* Type check: pass
* Tests: pass
* Coverage ≥ 85%
* Registry coverage = 100%
* No dependency diff

---

# 5. Implementation Steps (Ordered, Reversible)

### Step 1 — Create Plugin File

Create:

```
ezra/plugins/tesseract_plugin.py
```

Requirements:

* Minimal stub
* Conforms to existing plugin interface
* Does NOT call external binary
* Returns deterministic placeholder output
* No new third-party imports

**Locked Decisions:**
* `infer()` returns `{"detections": []}`
* `describe_capabilities()` returns `"version": "stub-0.0.1"`
* `load()` is a no-op
* `__init__(self, languages: list[str] | None = None)` only

---

### Step 2 — Static Registry Update

Update registry:

```
PLUGIN_REGISTRY = {
    "easyocr": EasyOCRPlugin,
    "tesseract": TesseractPlugin,
}
```

Must preserve deterministic ordering (easyocr first, tesseract appended).

---

### Step 3 — Add Tests

Add:

* `test_tesseract_plugin_loads`
* `test_registry_snapshot_updated`
* `test_unknown_plugin_error_unchanged`
* `test_tesseract_does_not_import_easyocr`

Do NOT modify parity tests.

---

### Step 4 — Run Coverage

Verify:

* Registry remains 100%
* Overall ≥ 85%

If registry coverage drops, fix tests immediately.

---

### Step 5 — CI Verification

Create PR:

Branch: `m06-tesseract-plugin`

Monitor:

* Lint
* Type Check
* Test

Generate `M06_run1.md` using workflow analysis prompt.

---

### Step 6 — Closeout Artifacts

After green CI:

Generate:

* `docs/milestones/M06/M06_summary.md`
* `docs/milestones/M06/M06_audit.md`
* `docs/milestones/M06/M06_run1.md`
* `docs/milestones/M06/M06_toolcalls.md`

Follow exact formatting from summary + audit prompts.

---

# 6. Risk & Rollback Plan

## Primary Risk

Accidental behavior drift in registry resolution.

## Rollback

* Revert registry diff
* Revert plugin file
* Restore snapshot
* Confirm parity tests green

No migration required.

---

# 7. Deliverables

Upon closure:

* New plugin file
* Updated registry
* Deterministic snapshot
* New tests
* CI run analysis
* Milestone summary
* Milestone audit
* Updated milestone table entry

---

# 8. Acceptance Criteria (Hard Gates)

All must be true:

* EasyOCR parity tests unchanged
* Registry deterministic
* No new dependencies
* CI green
* Coverage ≥ 85%
* Registry coverage = 100%
* No public API change
* Audit verdict = 🟢

---

# 9. Explicit Closeout Prompt for Cursor

When CI is green, use this exact instruction:

> Generate M06_summary.md using RefactorSummaryPrompt.md.
> Generate M06_audit.md using RefactorMilestoneAuditPrompt.md.
> Generate M06_run1.md using RefactorWorkflowPrompt.md.
> Merge branch into main.
> Tag v0.0.7-m06.
> Verify tag points to merge commit.
> Confirm post-merge CI green.
> Update milestone table in docs/ezra.md.
> Create M07 folder with stub M07_plan.md and M07_toolcalls.md.
> Do not push additional commits after closure.

---

# Why This Is the Correct Next Step

This milestone:

* Exercises the plugin boundary without orchestration complexity
* Proves extension safety
* Increases confidence in registry architecture
* Preserves behavior strictly
* Maintains audit score trajectory

It prepares the ground for:

* M07 — Engine Orchestration Layer
* M08 — Zone Abstraction Layer

