# M13 — Zone-Aware EPB Extension (Adapter-Gated, Behavior-Preserving)

## 1. Intent / Target

Introduce **zone-aware metadata wiring into the EPB emission pipeline**, strictly behind an adapter boundary, without altering:

* EPB v1.0.0 directory structure
* Canonicalization rules
* Hashing rules
* Runtime inference logic
* Plugin outputs

The objective is to:

> Allow EPB bundles to optionally embed a deterministic `zones` section derived from `ZoneRegistry`, while preserving full backward compatibility.

This milestone converts the zone contract from "locked structural primitive" (M12) into an **artifact-surface participant**, without expanding scope into perception logic.

---

## 2. Scope Boundaries

### In Scope

* Add optional `zones.json` to EPB bundle directory
* Zones are exported from `ZoneRegistry`
* Deterministic canonicalization preserved
* EPB hash verification updated to include zones file (if present)
* Adapter-based wiring (no direct runtime-zone coupling)
* Backward compatibility preserved

### Out of Scope

* No automatic zone detection
* No runtime logic that consumes zones
* No plugin modifications
* No change to EPB schema version
* No changes to canonical JSON rules
* No performance changes
* No change to inference pipeline
* No schema bump to EPB v2

---

## 3. Invariants (Must Not Change)

Inherited from M12:

1. CI remains truthful 
2. Determinism multi-run gate remains green 
3. EPB canonicalization rules unchanged 
4. EPB hashing algorithm unchanged 
5. No breaking API changes
6. Coverage ≥ baseline
7. Artifact-boundary-only RediAI integration 

New invariant introduced in M13:

8. If zones are included, bundle determinism must remain byte-identical across N≥3 runs.

---

## 4. Verification Plan

### Required Evidence

* All existing tests pass unchanged
* Determinism job passes
* Hash verification includes zones file deterministically
* Snapshot test for EPB-with-zones
* Snapshot test for EPB-without-zones
* CI artifact integrity preserved

### New Tests Required

1. `test_epb_with_empty_zones_registry`
2. `test_epb_with_populated_registry`
3. `test_epb_hash_includes_zones`
4. Determinism multi-run validation including zones
5. Backward compatibility test (legacy EPB without zones)

---

## 5. Implementation Steps (Strict Order)

### Step 1 — Adapter Surface

Create:

```
src/ezra/zones/epb_adapter.py
```

Responsibility:

* Accept `ZoneRegistry`
* Produce canonical JSON dict
* Return deterministic structure

No direct EPB import inside zones module.

---

### Step 2 — EPB Wiring (Optional Hook)

Modify EPB emission pipeline:

* If `ZoneRegistry` provided:

  * Emit `zones.json`
* If not:

  * Emit nothing (preserve legacy behavior)

Must not modify existing JSON structure of:

* manifest.json
* detections.json
* state.json
* delta.json
* hashes.json

Zones is additive only.

---

### Step 3 — Hash Inclusion

Update hash computation:

* If `zones.json` exists:

  * Include in SHA256 computation
* Must not alter hash rules for legacy bundles

Add test:

* Legacy bundle hash unchanged
* Zone-enabled bundle hash deterministic

---

### Step 4 — Determinism Hardening

Extend determinism gate to:

* Emit EPB with zones
* Compare across 3 runs
* Assert byte-identical bundles

---

### Step 5 — Contract Snapshot

Add:

```
tests/contracts/test_epb_zone_snapshot.py
```

Two snapshots:

* EPB baseline (no zones)
* EPB + zones

---

### Step 6 — Documentation Update

Update:

* `docs/specs/epb_v1/EPB_V1_SPEC.md`
* Clarify zones file is optional extension
* No schema version bump

---

## 6. Risk & Rollback Plan

### Primary Risk

Accidental mutation of canonicalization order or hashing.

### Mitigation

* Determinism gate remains blocking
* Snapshot tests committed
* Hash verification tests strict

### Rollback Strategy

* Remove adapter
* Remove zones.json emission
* Re-run determinism gate
* Re-tag minor version

No schema migration needed.

---

## 7. Deliverables

* `epb_adapter.py`
* Optional zones emission
* Deterministic inclusion in hash
* New contract tests
* CI run analysis
* M13_summary.md
* M13_audit.md
* No baseline drift
* No EPB version bump

---

## 8. Milestone Classification

Type: **Contract Surface Extension (Additive, Backward-Compatible)**
Posture: Behavior-preserving
Scope: Artifact-level extension only

---

## 9. Expected PR Title

```
refactor(epb): optional deterministic zone emission (M13)
```

---

## 10. Acceptance Criteria

* CI green on first run
* Determinism job green
* No coverage regression
* No changes to existing EPB schema fields
* Hash integrity preserved
* Snapshot tests committed
* Audit score ≥ 4.9

