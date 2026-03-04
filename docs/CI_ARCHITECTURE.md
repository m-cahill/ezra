# EZRA CI Architecture

EZRA CI is designed to enforce determinism, artifact integrity, and supply-chain security.

## CI Tiers

### Tier 1 — PR Validation (required)

Executed on pull_request:

- Ruff lint
- Pydocstyle
- Mypy
- Pytest (coverage ≥ 85%)
- EPB tools minimal environment
- SBOM generation
- Bandit / pip-audit / gitleaks
- Radon complexity gate
- Determinism check (triple run)
- Hermetic hash matrix (Python 3.10 / 3.11 / 3.12)
- Hermetic reproducibility check
- Documentation build

These checks must pass before merge.

---

### Tier 2 — Supply Chain Integrity

Informational checks:

- OpenSSF Scorecard
- Dependency Review

Currently non-blocking due to repository infrastructure constraints.

---

### Tier 3 — Release Workflow

Triggered only on:

```yaml
push:
  tags:
    - "v*"
```

Steps:

1. Build reproducible sdist + wheel
2. Generate artifact hashes
3. Generate CycloneDX SBOM
4. Generate SLSA provenance
5. Publish to PyPI using OIDC Trusted Publishing

Release CI does **not run during PR validation**.
