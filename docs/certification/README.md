# EZRA Certification

This directory holds documentation related to EZRA’s **certification posture** and artifact trust boundary.

## Overview

- **EZRA** emits EPB (EZRA Perception Bundle) v1.0.0 artifacts. It does not perform certification itself.
- **RediAI v3** (and other consumers) certify EPB bundles: they validate schema, hashes, and optional signatures. Integration is **artifact-boundary-only**; no shared code or runtime.

See the project operating manual for the canonical description:

- **RediAI separation & certification:** `docs/ezra.md` §10 (RediAI Separation & Certification Posture)
- **EPB specification and schemas:** `docs/specs/epb_v1/EPB_V1_SPEC.md` and `docs/specs/epb_v1/schemas/`
- **Phase V completion and artifact contract:** `docs/phase_v_completion_declaration.md`

## EZRA-Side Certification-Relevant Artifacts

| Milestone | Deliverable | Purpose |
|-----------|-------------|---------|
| M25 | `epb_certify` (stdlib-only) | Consumer certification harness; validate bundle structure, hash integrity, bundle hash without EZRA runtime |
| M26 | `epb_sign` / `epb_verify` | Detached Ed25519 signing and verification; optional cryptographic attestation |
| M27 | `epb_generate_cert_metadata` | Detached certification metadata envelope (`bundle.cert.json`) for archival and compliance |
| M28 | `ezra.epb_tools` namespace | Physical isolation of EPB tools; no runtime/plugin/ML import required for certification, signing, verification |

## Consumer Certification Flow

1. EZRA emits an EPB bundle (deterministic, canonicalized per EPB v1.0.0).
2. Consumer (e.g. RediAI v3) validates the bundle against JSON schemas and verifies `hashes.json`.
3. Consumer may verify optional `bundle.sig` and use `bundle.cert.json` for attestation evidence.

**No runtime integration.** All interaction is at the artifact boundary.
