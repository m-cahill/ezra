# M17 — Release Lock Program (Phase V Initiation)

## 1. Intent / Target

M17 initiates **Phase V — Release Lock**.

Objective:
Formally freeze EZRA's public runtime surfaces, EPB contract, and exception taxonomy,
and introduce structural guardrails that prevent accidental drift.

This milestone introduces:
- Public surface inventory
- API freeze declaration
- Schema freeze declaration
- Exception taxonomy freeze declaration
- Automated surface drift detection (lightweight)

NO runtime behavior changes.
NO schema changes.
NO feature expansion.
NO new dependencies.

---

## 2. Scope Boundaries

### In Scope
- Public API inventory (explicit list)
- Exception taxonomy freeze declaration
- EPB v1.0.0 freeze declaration (formalized)
- Minimal automated public surface diff test
- Documentation hardening

### Out of Scope
- Any runtime logic change
- EPB schema modification
- Plugin changes
- Performance work
- Logging framework
- Artifact structure change
- New CI gates beyond minimal surface check

---

## 3. Invariants (Must Not Change)

The following MUST remain true:

1. All 213 tests pass (205 original + 8 M16 tests).
2. 4 skipped tests remain skipped.
3. Determinism gate passes.
4. EPB v1.0.0 schema unchanged.
5. Hash algorithm unchanged.
6. Exception hierarchy structure unchanged.
7. Coverage ≥ baseline (95%+).
8. All 7 CI jobs remain green.
9. No new required CI jobs added.

---

## 4. Verification Plan

### A. Public Surface Snapshot

Introduce a test that:

- Inspects `ezra` package exports.
- Snapshots:
  - `__all__` (if defined)
  - Exception hierarchy tree
  - Public module list under `src/ezra/`
- Writes canonical sorted JSON snapshot.

If surface changes, test fails.

### B. Exception Taxonomy Freeze Test

Test must assert:

- Exact class names present.
- Inheritance structure intact.
- No new subclasses under `EzraError` without explicit milestone update.

### C. EPB Contract Freeze Assertion

Add assertion test:

- `epb_version == "1.0.0"`
- Schema directory checksum snapshot

This prevents silent schema drift.

### D. CI Confirmation

Run full suite.
Confirm no drift.
Confirm determinism.

---

## 5. Implementation Steps

1. Create `tests/test_public_surface_freeze.py`
2. Add helper for canonical JSON snapshot.
3. Snapshot:
   - Module exports
   - Exception hierarchy structure
   - EPB version constant
4. Store snapshot under:
   `docs/baselines/public_surface_snapshot.json`
5. Add deterministic serialization.
6. Run tests locally.
7. Update snapshot once (expected initial generation).
8. Run CI.
9. Produce M17_run1.md.
10. If green → proceed to audit.

---

## 6. Risk & Rollback Plan

### Risk
- Snapshot too broad → causes noise.
- Overly strict freeze prevents future milestones.

### Mitigation
- Snapshot only:
  - Module names
  - Exception tree
  - EPB version
- No deep introspection.
- Document update procedure clearly.

### Rollback
Revert snapshot test + baseline file.
No runtime code touched.

---

## 7. Deliverables

- `tests/test_public_surface_freeze.py`
- `docs/baselines/public_surface_snapshot.json`
- `docs/milestones/M17/M17_run1.md`
- `docs/milestones/M17/M17_audit.md`
- `docs/milestones/M17/M17_summary.md`
- Tag: `v0.0.18-m17`

---

## Exit Criteria

- All 7 CI jobs pass.
- Snapshot test passes.
- No behavior drift.
- No schema drift.
- No exception taxonomy drift.
- Determinism preserved.
- Working tree clean.

---

## Strategic Outcome

After M17:

EZRA becomes:

- Public-surface frozen
- EPB contract frozen
- Exception taxonomy frozen
- Deterministic
- CI-evidence producing
- Release-candidate ready

M17 transitions EZRA into **v1.0.0-rc posture**.
