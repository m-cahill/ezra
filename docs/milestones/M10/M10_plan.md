# 📌 M10_plan — JSON Schema Validation Wiring (EPB Hardening Phase 2)

---

## 1. Intent / Target

**Primary Objective:**
Wire JSON Schema validation into EPB bundle emission flow to guarantee schema validity before hash computation and file writing.

M09 delivered:
* Determinism multi-run CI gate
* Byte-identical bundle verification
* Timestamp injection capability

However:
* JSON Schemas exist (defined in M07) but are not validated at runtime
* Schema validation is currently implicit (test coverage only)
* Schema violations could be emitted without detection

This milestone converts schema validation from "implicitly covered" → **explicit runtime guardrail**.

---

## 2. Scope Boundaries

### ✅ In Scope

* JSON Schema validation wiring
* Runtime schema validation in emission flow
* Validation error handling
* CI validation gate (if applicable)
* Schema validation tests

### ❌ Out of Scope

* Schema changes
* New schema definitions
* Performance optimization
* Refactoring unrelated modules
* Coverage threshold changes

---

## 3. Refactor Posture

**Behavior-Preserving**

No externally observable behavior changes are authorized.

The milestone introduces:
* Schema validation checks
* Validation error handling
* Validation tests

It must not:
* Change bundle format
* Change validation rules
* Modify serialization behavior

If validation fails, emission must fail — not auto-fix.

---

## 4. Invariants (Mandatory)

### Invariant 1 — Schema Validation

EPB bundles must validate against JSON Schemas before hash computation and writing.

**Verification:**
* Validation runs before hashing
* Invalid bundles fail emission
* Validation errors are explicit

### Invariant 2 — No Silent Validation Bypass

Validation must not be skipped or muted.

**Verification:**
* No `continue-on-error` for validation
* Validation failures fail CI
* No silent validation bypass

### Invariant 3 — CI Signal Integrity

If validation fails:
* CI job fails
* No continue-on-error
* No muted failure

**Verification:**
* Validation job marked required
* Branch protection includes job (if applicable)

---

## 5. Implementation Steps (Ordered & Reversible)

### Step 1 — Schema Validation Module

Add:
```
src/ezra/epb/validator.py
```

Responsibilities:
* Load JSON Schemas
* Validate bundle components
* Raise explicit validation errors

### Step 2 — Wire Validation into Emission

Modify:
* `src/ezra/epb/writer.py` — Add validation before writing
* Or `src/ezra/epb/builder.py` — Add validation after building

### Step 3 — Add Validation Tests

Add:
* Unit tests for validation
* Invalid bundle tests
* Schema loading tests

### Step 4 — CI Validation Gate (Optional)

If applicable:
* Add validation job or step
* Upload validation artifacts
* Report validation results

---

## 6. Definition of Done

* Schema validation wired into emission flow
* Invalid bundles fail emission
* Validation tests added
* No coverage regression
* CI green with validation
* Audit passes
* Tag created after merge

---

**Note:** This is a stub plan. Full implementation details will be developed during milestone execution.

