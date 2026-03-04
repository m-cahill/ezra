# M26_plan — EPB Artifact Signing & Verification (Detached Ed25519)

---

## 1. Intent / Target

**Primary Objective:** Introduce **detached cryptographic signing and verification** for EPB bundles using Ed25519.

After M25, EPB is: structurally locked, deterministically reproducible, externally certifiable (hash integrity + bundle hash). M26 adds **cryptographic attestability**.

This milestone remains: behavior-preserving, no EPB schema changes, no emission logic changes, additive tooling only.

---

## 2. Scope

### In Scope

- `epb_sign.py` — Detached signature generation
- `epb_verify.py` — Detached signature verification
- Ed25519 via `cryptography` library
- Signature file: `bundle.sig` (default) or `--sig-path` override; JSON format with algorithm, bundle_hash, signature, public_key
- Tests: sign+verify success, tampered bundle fails, wrong key fails
- CI integration (step in Test job)
- Governance docs update
- Closeout artifacts

### Out of Scope

- No signature embedded into EPB directory
- No EPB schema change
- No auto-signing in emission pipeline
- No key management infrastructure / PKI / trust-chain / hardware key support

---

## 3. Invariants (Must Not Change)

- EPB structure (M24)
- Determinism (M24 + M25)
- Artifact self-consistency (M25): signature over canonical bundle hash only
- Consumer-isolated validation: `epb_sign.py` and `epb_verify.py` use stdlib + `cryptography` only; no `ezra.core` / `ezra.epb` imports
- CI truthfulness: new step required; no weakening of existing checks

---

## 4. Technical Design

- **Signing payload:** SHA256(bundle) — the canonical bundle hash (same as M25 certifier).
- **Signature file:** `bundle.sig` (JSON): `algorithm`, `bundle_hash`, `signature` (base64), `public_key` (base64).
- **Key interface:** Ephemeral keypair by default; optional `--private-key <path>` for caller-provided key; no automatic private key persistence.

---

## 5. Locked Decisions (from clarification)

- Cryptography: exact pin in pyproject.toml (e.g. `cryptography==46.0.5`).
- Signature file default: `bundle.sig`; optional `--sig-path`.
- epb_sign: stdlib + cryptography only; bundle hash via shared stdlib-only helper.
- epb_verify: stdlib + cryptography only; same helper for recomputing bundle hash.

---

## 6. Deliverables

- `M26_plan.md`, `M26_run1.md`, `M26_audit.md`, `M26_summary.md`
- `src/ezra/tools/epb_sign.py`, `src/ezra/tools/epb_verify.py`
- Stdlib-only bundle-hash helper (for sign/verify)
- `tests/contracts/test_epb_artifact_signing.py`
- CI step "EPB Artifact Signing"
- Ledger update in `docs/ezra.md`

---

## 7. Exit Criteria

- Sign + verify works; tamper detection fails verification; wrong-key fails verification
- CI 9/9 required checks passing
- Coverage unchanged or improved
- No invariant drift
- Audit verdict 🟢 or 🟡 (no HIGH issues)
