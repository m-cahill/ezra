# M25 Plan — EPB Consumer Certification & Artifact Reproducibility Hardening

Anchored to M24 audit and M24 summary. Assumes EPB artifact boundary is contract-locked, determinism enforced at workflow + test layer, CI guardrails strict. Phase V — Release Lock posture.

---

## 1. Intent / Target

**Primary objective:** Introduce a formal, reproducible **EPB Consumer Certification harness** that validates:

1. EPB bundle is reproducible across clean environments
2. EPB artifact is self-consistent (internal hash integrity)
3. Consumer validation can be executed without importing EZRA internals

This milestone strengthens: artifact portability, external consumer trust, long-term archival reproducibility, supply-chain defensibility, extraction readiness.

**Behavior-preserving.** No runtime logic changes. No EPB schema changes. No public API changes.

---

## 2. Scope

**In scope:** `epb_certify.py` (stdlib-only), `tests/contracts/test_epb_consumer_certification.py`, reproducibility verification (temp dir teardown + re-emit), artifact self-consistency (hash ledger cross-check), CI step “EPB Consumer Certification”, docs (M25 plan/run/audit/summary).

**Out of scope:** No EPB schema changes, no runtime emission logic changes, no dependency upgrades, no performance tuning, no cryptographic algorithm swaps, no artifact signing (M26+).

---

## 3. Invariants (unchanged)

- EPB structural contract (M24)
- Determinism (M24)
- **New:** Artifact self-consistency — `hashes.json` matches actual file digests; bundle hash matches recomputed hash
- **New:** Consumer-isolated validation — certifier uses only Python stdlib (no EZRA imports)

---

## 4. Verification

- **Artifact self-consistency:** Build bundle, certify; assert `certify(bundle).hash_integrity_passed` (and bundle_hash_valid).
- **Consumer-isolated:** Subprocess `python -m ezra.tools.epb_certify <bundle>`; exit 0, structured JSON summary.
- **Reproducibility:** Emit to `tmp_path/"a"`, rmtree, emit to `tmp_path/"b"`, compare canonical digests (bundle_hash).
- **CI:** New step in Test job after EPB Contract Harness; failure blocks merge.

---

## 5. Implementation steps

1. Create branch `m25-epb-consumer-certification`
2. Add `src/ezra/tools/epb_certify.py`
3. Add `tests/contracts/test_epb_consumer_certification.py`
4. Wire certification into CI Test job
5. Run full CI; generate M25_run1.md, open PR, then M25_audit.md and M25_summary.md

---

## 6. Locked decisions (from handoff)

- **Invocation:** `python -m ezra.tools.epb_certify <bundle_path>`; JSON to stdout only; exit 0/1.
- **Certifier:** Stdlib only (json, hashlib, pathlib, argparse, sys, math). No ezra.* imports.
- **Reproducibility test:** Emit to a, rmtree a, emit to b; compare bundle hashes (no new interpreter).
- **CI:** Single new step in Test job after EPB Contract Harness; summary section “EPB Consumer Certification”.

---

## 7. Exit criteria

- 100% EPB self-consistency verified
- Consumer certification runs in isolation (subprocess)
- CI 9/9 required checks passing
- Coverage unchanged or improved
- No invariant drift
- Audit verdict green or yellow (no HIGH issues)
