# 📦 M22_plan — Zone Schema Evolution Guardrails & Diff Governance

## 1. Intent / Target

### Primary Objective

Now that the Universal Zone Mapping Schema (UZMS) is:

* Formally defined (`schema_v1.json`)
* Versioned (`SCHEMA_VERSION = "1.0.0"`)
* CI-validated
* Contract-tested

M22 introduces **schema evolution governance and diff discipline**, without changing runtime behavior.

We will:

1. Add a **Schema Evolution Policy** (machine + doc enforced)
2. Add a **schema diff guardrail** in CI
3. Add a **breaking-change detection test**
4. Add a version bump enforcement rule
5. Add documentation describing versioning semantics

---

### Why This Milestone Exists

M21 locked the contract.

M22 prevents silent drift.

Right now:

* `schema_v1.json` exists.
* `SCHEMA_VERSION = "1.0.0"` exists.
* CI validates shape.

But nothing prevents:

* Field removal without version bump
* Constraint tightening without documentation
* Silent incompatible changes

M22 ensures:

> Any schema change requires explicit versioning and review.

---

## 2. Scope Boundaries

### In Scope

* Add schema version enforcement tests
* Add JSON Schema diff detection in CI
* Add semantic version validation rule
* Add governance documentation section
* No runtime behavior change

---

### Out of Scope

* No changes to schema structure
* No runtime modifications
* No plugin changes
* No EPB changes
* No performance work
* No new features
* No schema v2 introduction

This is a governance hardening milestone.

---

## 3. Refactor Posture

**Behavior-Preserving**

The following must remain unchanged:

* Zone serialization output
* Schema contents
* Zone registry logic
* Determinism guarantees
* Plugin interfaces
* Public surfaces

No runtime code logic changes allowed.

---

## 4. Invariants (Must Hold)

### I1 — Schema Content Stability

`schema_v1.json` must not change without:

* `SCHEMA_VERSION` bump
* Explicit milestone documentation

---

### I2 — Version-Schema Coupling

If `schema_v1.json` changes:

* `SCHEMA_VERSION` must change
* CI must fail otherwise

---

### I3 — No Breaking Changes Without Explicit Acknowledgment

Removing fields or tightening constraints must:

* Fail CI unless explicitly authorized via version bump

---

### I4 — Determinism Unaffected

Schema governance must not alter:

* Zone serialization output
* Canonical JSON output

---

## 5. Implementation Steps (Ordered)

### Step 1 — Add Schema Snapshot Baseline

Create:

```
docs/baselines/zone_schema_snapshot.json
```

This is a committed canonical copy of `schema_v1.json`.

Purpose:

* CI diff detection
* Drift guardrail

---

### Step 2 — Add Schema Diff Test

Create:

```
tests/test_zone_schema_diff.py
```

Behavior:

* Load `schema_v1.json`
* Load baseline snapshot
* Compare canonical JSON
* Fail if mismatch

Unless version bump present.

---

### Step 3 — Add Version Coupling Test

Create:

```
tests/test_zone_schema_version_enforcement.py
```

Rules:

* If schema changed AND `SCHEMA_VERSION` unchanged → fail
* If schema unchanged AND version changed → fail

---

### Step 4 — Add CI Guardrail Step

Add step in CI:

```
Validate schema snapshot unchanged
```

Visible in job summary:

```
## Schema Governance
- Snapshot match: PASS
- Version coupling: PASS
```

---

### Step 5 — Add Governance Documentation

Update:

```
docs/architecture/zones.md
```

Add section:

```
## Schema Evolution Policy
```

Define:

* Backward-compatible change rules
* Version bump rules
* Deprecation rules
* Prohibited changes
* Required milestone posture for schema changes

---

## 6. Verification Plan

### Local

* All tests pass
* No coverage drop
* Determinism unchanged
* No snapshot drift

---

### CI

Must confirm:

* All required jobs pass
* Schema governance section visible
* No weakening of existing checks
* Coverage ≥ baseline

---

## 7. Risk & Rollback

### Risk

* False positives if JSON formatting inconsistent

Mitigation:

* Use canonical JSON ordering for diff

---

Rollback Plan:

* Single revert of M22 branch
* No schema changes introduced

---

## 8. Deliverables

M22 must produce:

* `docs/baselines/zone_schema_snapshot.json`
* `tests/test_zone_schema_diff.py`
* `tests/test_zone_schema_version_enforcement.py`
* CI update
* Documentation update
* `M22_summary.md`
* `M22_audit.md`
* `M22_run1.md`

---

## 9. Definition of Done

M22 is complete when:

* Schema diff enforcement active
* Version bump enforcement active
* CI green
* No behavior drift
* Coverage unchanged
* Determinism intact
* Audit verdict PASS
* Ledger updated

---

## 10. Audit Mode

```
Mode: DELTA AUDIT
Posture: Behavior-Preserving
Focus: Governance & Schema Evolution Discipline
```
