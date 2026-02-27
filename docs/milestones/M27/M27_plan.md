# M27_plan — Detached Certification Metadata Layer

---

## 1. Intent / Target

After M26 and M29, EPB bundles are: structurally locked, deterministic, snapshot-protected, externally certifiable, cryptographically signed, and hermetically reproducible.

Certification artifacts (hashes, signature, validation results) are scattered: `hashes.json` (inside bundle), `bundle.sig` (detached signature), certification output (stdout JSON).

M27 introduces a **detached, structured Certification Metadata Envelope** (`bundle.cert.json`) that aggregates verification results in a standardized archival format. Enables long-term archival, compliance workflows, external artifact indexing, and third-party verification pipelines.

No EPB schema change. No emission change. No canonicalization change. Additive tooling only.

---

## 2. Scope

### In Scope

- New tool: `epb_generate_cert_metadata.py`
- Output file: `bundle.cert.json`
- Metadata envelope: nested sections only (see Locked Decisions)
- Contract tests: metadata_valid_structure, metadata_invalid_if_tampered (payload + hashes.json + optional signature), metadata_no_signature_case
- CI step: "EPB Certification Metadata" (required, in Test job)
- Documentation update

### Out of Scope

- No embedding into EPB directory
- No schema modification
- No runtime changes
- No new dependencies
- No PKI chain validation
- No revocation model

---

## 3. Invariants

| Invariant                | Must Remain |
| ------------------------ | ----------- |
| EPB v1.0.0 schema frozen | Yes         |
| Canonicalization rules   | Yes         |
| Hashing rules            | Yes         |
| Signing rules            | Yes         |
| Hermetic reproducibility | Yes         |

---

## 4. Certification Metadata Format (Locked)

Canonical shape (nested sections only; no duplicate top-level booleans):

```json
{
  "epb_version": "1.0.0",
  "bundle_hash": "<hex>",
  "certification": {
    "structure_valid": true,
    "hash_integrity_valid": true,
    "bundle_hash_valid": true
  },
  "signature": {
    "present": true,
    "valid": true,
    "algorithm": "ed25519"
  },
  "environment": {
    "python_version": "3.11.8",
    "certifier_version": "v0.0.29-m27"
  },
  "generated_at_utc": "2026-02-27T21:14:00Z"
}
```

Canonical JSON rules apply (sorted keys, UTF-8, LF).

---

## 5. Locked Decisions

1. **Metadata shape:** Nested sections only; no duplicate top-level booleans.
2. **certifier_version:** From `ezra.__version__` if present; else installed package metadata; fallback `"unknown"`. No PR/commit injection.
3. **Missing signature:** Do not hard-fail. `present: false`, `valid: false` when no sig; hard-fail only on structure invalid or hash integrity invalid.
4. **CI:** Step "EPB Certification Metadata" in existing Test job; required; runs on every PR.
5. **Tamper tests:** (A) Payload mutation → hash_integrity_valid false, bundle_hash_valid false; (B) hashes.json mutation only → same; (C) optional signature mutation → present true, valid false.

---

## 6. Implementation Steps

1. Create branch `m27-detached-cert-metadata`
2. Create `src/ezra/tools/epb_generate_cert_metadata.py`
3. Use stdlib + existing tools (certify, verify_bundle); certifier_version from canonical source
4. Contract tests + CI step + milestone scaffold
5. Update `docs/ezra.md` on closeout

---

## 7. Exit Criteria

- Metadata file generated correctly
- Signing + certification integration verified
- Tampered bundle produces invalid metadata
- CI 9/9 required checks passing
- No runtime/schema changes
- Audit verdict 🟢

---

## 8. Guardrails

- No edits under `src/ezra/core/`
- No edits under `docs/specs/epb_v1/`
- No edits to canonicalization or hashing logic
- No dependency changes
- No coverage drop > 0.1%
