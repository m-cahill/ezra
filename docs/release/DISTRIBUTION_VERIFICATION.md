# Distribution Verification

This document describes how EZRA verifies that distribution artifacts produced by the release workflow are **deterministic**, **reproducible**, and **cryptographically verifiable**.

---

## Purpose

The release workflow (triggered by pushing a `v*` tag) builds sdist and wheel, records artifact hashes in `dist/SHA256SUMS.txt`, generates a CycloneDX SBOM, and produces provenance metadata. The **distribution verification** script and CI job ensure that:

1. Recorded hashes match the actual artifact files.
2. A local rebuild (`python -m build`) produces identical hashes.
3. The SBOM is valid and dependency list is present.
4. Provenance contains commit, builder, workflow, and artifact hashes.

This gives supply-chain transparency and proves that releases are reproducible from source.

---

## Verification Steps

1. **Resolve tag** — Use `--tag vX.Y.Z` or `--tag latest` (most recent release run).
2. **Resolve workflow run** — Find the completed Release workflow run for that tag.
3. **Download artifacts** — Fetch `ezra-distribution`, `ezra-sbom`, and `ezra-provenance` from that run.
4. **Verify artifact hashes** — Compare `SHA256SUMS.txt` with hashes of the downloaded wheel and sdist.
5. **Rebuild locally** — Run `python -m build` and compare hashes with the release artifacts.
6. **Validate SBOM** — Ensure `sbom.json` is valid JSON with a non-empty dependency/component list.
7. **Validate provenance** — Ensure `provenance.json` contains `commit`, `builder`, `workflow`, and `artifact_hashes`.
8. **Emit report** — Print a JSON report with `distribution_verified: true` only if all checks pass.

---

## Security Model

- **Reproducible builds** — Same source and tooling produce the same artifacts; the verifier rebuilds and compares hashes.
- **OIDC publishing** — PyPI Trusted Publishing uses OIDC; no long-lived tokens. See [PYPI_TRUSTED_PUBLISHING.md](PYPI_TRUSTED_PUBLISHING.md).
- **Artifact hashing** — Every release records SHA256 of wheel and sdist in `dist/SHA256SUMS.txt`; the verifier confirms files match.
- **SBOM transparency** — CycloneDX SBOM (`dist/sbom.json`) lists dependencies; the verifier checks structure and presence.
- **Provenance attestation** — The release workflow writes `provenance.json` (commit, builder, workflow, artifact hashes) and uploads it as `ezra-provenance`; the verifier validates required fields.

No cryptographic verification of attestations is required in this milestone; the focus is on structural validation and hash consistency.

---

## Example Verification

Verify the release for a specific tag (requires `GITHUB_TOKEN` and `GITHUB_REPOSITORY` or `--repo`):

```bash
python scripts/verify_distribution.py --tag v1.0.1-m33
```

Verify the latest release (used by CI):

```bash
python scripts/verify_distribution.py --tag latest
```

Example output (success):

```json
{
  "artifact_hashes_match": true,
  "distribution_verified": true,
  "rebuild_hash_match": true,
  "sbom_valid": true,
  "provenance_valid": true,
  "tag": "v1.0.1-m33"
}
```

Exit code `0` means distribution verified; `1` means a check failed; `2` means error (e.g. missing token or run not found).

---

## CI

The **Distribution Verification** job runs on pull requests, push to `main`, and `workflow_dispatch`. It uses `--tag latest` and does not block merges (non-required check). It requires `GITHUB_TOKEN` and installs `build` to perform the local rebuild.
