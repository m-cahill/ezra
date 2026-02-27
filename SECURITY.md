# Security Policy

## Supported Versions

EZRA is currently in pre-alpha development. Security updates will be provided for the latest release.

| Version | Supported          |
| ------- | ------------------ |
| 0.0.x   | :white_check_mark: |

## Reporting a Vulnerability

Please report security vulnerabilities to the project maintainers via GitHub Security Advisories or by emailing the repository owner.

**Do not** open public issues for security vulnerabilities.

## Security Practices

EZRA follows the **NIST Secure Software Development Framework (SSDF) SP 800-218** and aligns with **OWASP Application Security Verification Standard (ASVS) Level 2** practices.

### SSDF SP 800-218 Mapping

| SSDF Practice | EZRA Implementation | Evidence |
|--------------|---------------------|----------|
| **PO.3.1** — Protect all forms of code from unauthorized access | Gitleaks full-repo scan in CI | `.github/workflows/ci.yml` (security job) |
| **PO.3.2** — Maintain provenance data | SBOM generation + SLSA provenance attestation | `.github/workflows/ci.yml` (sbom, provenance jobs) |
| **PS.1.1** — Create source code by adhering to secure coding practices | Bandit static security analysis | `.github/workflows/ci.yml` (security job) |
| **PS.3.1** — Create and maintain provenance information | CycloneDX SBOM + SLSA attestations | `.github/workflows/ci.yml` (sbom, provenance jobs) |
| **PW.7.1** — Verify that vulnerabilities are addressed | pip-audit dependency scanning (strict mode) | `.github/workflows/ci.yml` (security job) |
| **PW.7.2** — Verify that code does not contain malicious functionality | Bandit + Gitleaks security scanning | `.github/workflows/ci.yml` (security job) |
| **PW.8.1** — Verify that code is traceable | Test coverage ≥ 85% (lines and branches) | `.github/workflows/ci.yml` (test job) |
| **PW.8.2** — Verify that code is maintainable | Radon complexity gate (grade C minimum) | `.github/workflows/ci.yml` (complexity job) |
| **RV.1.1** — Identify and confirm vulnerabilities | pip-audit + Bandit vulnerability scanning | `.github/workflows/ci.yml` (security job) |
| **RV.1.2** — Assess and prioritize vulnerabilities | Bandit severity levels (HIGH enforcement) | `.github/workflows/ci.yml` (security job) |

### OWASP ASVS Level 2 Mapping

| ASVS Requirement | EZRA Implementation | Evidence |
|------------------|---------------------|----------|
| **V1.1.1** — Verify use of up-to-date and trusted components | pip-audit dependency vulnerability scanning | `.github/workflows/ci.yml` (security job) |
| **V1.2.1** — Verify that all components are inventory | CycloneDX SBOM generation | `.github/workflows/ci.yml` (sbom job) |
| **V1.2.2** — Verify that all components are analyzed for vulnerabilities | pip-audit dependency scanning | `.github/workflows/ci.yml` (security job) |
| **V7.1.1** — Verify that all code is maintained | Test coverage ≥ 85% | `.github/workflows/ci.yml` (test job) |
| **V7.2.1** — Verify that code complexity is managed | Radon complexity gate (grade C) | `.github/workflows/ci.yml` (complexity job) |
| **V14.2.1** — Verify that secrets are not hardcoded | Gitleaks secret detection (full-repo scan) | `.github/workflows/ci.yml` (security job) |

### Additional Security Measures

- **OpenSSF Scorecard** — Automated security posture assessment (warn-first, non-blocking)
- **Dependency Review** — Automated dependency change review on pull requests
- **SLSA Provenance** — Build attestation for supply chain integrity (main branch + tags)
- **Pre-commit hooks** — Local security checks before commit (gitleaks, bandit basic checks)

## Security Artifacts

Security evidence artifacts are generated in CI and available in workflow runs:

- `bandit.json` — Static security analysis report
- `pip_audit.json` — Dependency vulnerability report
- `gitleaks-results.sarif` — Secret detection report (SARIF format)
- `scorecard-results.sarif` — OpenSSF Scorecard results (SARIF format)
- `sbom.cdx.json` — Software Bill of Materials (CycloneDX JSON)

See `docs/qa.md` for detailed information about quality gates and artifact locations.

---

**Last Updated:** M18 (2026-02-27)  
**Maintainer:** EZRA Governance

