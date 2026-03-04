# M29_plan — Hermetic Reproducibility Gate (Matrix Determinism Enforcement)

---

## 1. Intent / Target

**Primary Objective:** Elevate EPB reproducibility from single-environment determinism (M24/M25) to **cross-environment hermetic reproducibility**.

After M26, EPB bundles are:

- Structurally locked
- Deterministically reproducible (single environment)
- Externally certifiable
- Cryptographically attestable

M29 ensures canonical bundle hash equivalence across Python versions.

This is the final piece required for:

- Research-grade reproducibility
- Artifact archival guarantees
- Long-term governance defensibility

Milestone posture:

- Behavior-preserving
- No schema changes
- No emission logic changes
- CI-only + verification enhancements

---

## 2. Scope Definition

### In Scope

1. Add CI matrix:
   - Python 3.10
   - Python 3.11
   - Python 3.12
2. Add canonical bundle-hash equivalence test across matrix
3. Add explicit "Hermetic Reproducibility" CI step
4. Fail build if hashes diverge
5. Update `docs/ezra.md`
6. Generate closeout artifacts

### Out of Scope

- No cross-OS matrix (unless explicitly authorized)
- No Docker-level hermeticity
- No reproducible wheels
- No container images
- No dependency changes

We are testing Python-version-level determinism only.

---

## 3. Invariants (Must Not Change)

1. **EPB Structure (M24)**  
   Verified via existing harness.

2. **Determinism (M24/M25)**  
   Single-environment determinism must remain passing.

3. **Artifact Self-Consistency (M25)**  
   Hash integrity must remain stable.

4. **Signature Validity (M26)**  
   Signing must still validate under matrix.

5. **Hermetic Equivalence (New)**  
   Canonical bundle hash must be identical across all matrix environments.

Verification requirements:

- Persist canonical bundle hash as artifact
- Compare across matrix jobs
- Fail if mismatch

---

## 4. Technical Design

### Strategy

Each matrix job:

1. Install project
2. Emit canonical EPB from fixed deterministic fixture
3. Compute canonical bundle hash
4. Write hash to file: `hermetic_hash.txt`
5. Upload as workflow artifact

Final job:

- Download all artifacts
- Compare all hashes
- Fail if any mismatch

### Why This Works

If the following are truly hermetic, bundle hash will match exactly:

- JSON canonicalization
- Float formatting
- Sorting
- Encoding
- Hash computation

If not:

- We detect subtle environment drift
- Before release
- Under CI

---

## 5. CI Changes

Modify `.github/workflows/ci.yml`:

Add matrix:

```yaml
strategy:
  matrix:
    python-version: [3.10, 3.11, 3.12]
```

Add comparison job:

```yaml
hermetic-reproducibility:
  needs: [test]
  runs-on: ubuntu-latest
```

Include artifact upload/download logic.

All jobs required.

No `continue-on-error`.

---

## 6. Implementation Steps (Ordered, Reversible)

1. Create branch: `m29-hermetic-reproducibility`
2. Update CI matrix
3. Add hermetic hash step
4. Add artifact comparison job
5. Add local reproducibility test helper (optional)
6. Run CI
7. Generate `M29_run1.md`
8. Open PR
9. Monitor CI
10. Generate `M29_audit.md`
11. Generate `M29_summary.md`
12. Update `docs/ezra.md`

---

## 7. Risk & Rollback

### Risk 1: Float formatting differences

Mitigation:

- Ensure canonical formatting already enforced (8dp/6dp logic)

### Risk 2: JSON ordering drift

Mitigation:

- Confirm sorted keys enforced

### Risk 3: Dependency-induced drift

Mitigation:

- Dependency pinning already in place

Rollback:

- Revert CI matrix changes

No runtime changes affected.

---

## 8. Deliverables

- `docs/milestones/M29/M29_plan.md`
- `M29_run1.md`
- `M29_audit.md`
- `M29_summary.md`
- CI matrix update
- Hash comparison job
- Ledger update

---

## 9. Exit Criteria

Milestone closes only if:

- Canonical bundle hash identical across Python 3.10/3.11/3.12
- CI required checks passing
- Coverage unchanged or improved
- No invariant drift
- Audit verdict 🟢 or 🟡 (no HIGH unresolved)

---

## Strategic Outcome After M29

EZRA artifact posture becomes:

- Schema locked
- Registry locked
- Deterministic
- Snapshot protected
- Externally certifiable
- Cryptographically attestable
- Hermetically reproducible across environments

At that point, Phase V is complete.
