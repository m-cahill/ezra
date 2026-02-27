# EZRA Quality Assurance & Governance

This document describes EZRA's quality gates, how to reproduce them locally, and their alignment with enterprise governance frameworks.

---

## Quality Gates Overview

EZRA's CI pipeline enforces a deterministic quality envelope through the following gates:

1. **Lint** — Code style and formatting consistency (ruff, pydocstyle)
2. **Type Check** — Static type analysis (mypy)
3. **Test** — Unit and integration test execution with coverage requirements
4. **Complexity** — Cyclomatic complexity analysis (radon)
5. **Security** — Static security analysis (bandit, pip-audit, gitleaks)
6. **SBOM** — Software Bill of Materials generation
7. **Determinism** — Byte-identical bundle verification across multiple runs
8. **Dependency Review** — Automated dependency change review (PR-only)
9. **OpenSSF Scorecard** — Security posture assessment (warn-first, non-blocking)
10. **SLSA Provenance** — Build attestation for supply chain integrity

---

## Gate Details

### 1. Lint Gate

**Tools:** `ruff`, `pydocstyle`  
**Enforcement:** Fail on any style violations  
**Configuration:** `pyproject.toml` `[tool.ruff]` and `[tool.pydocstyle]` sections

**What it enforces:**
- Code style consistency (PEP 8 alignment)
- Import sorting
- Unused imports/variables
- Code formatting (black-compatible)
- Docstring compliance (Google convention, src/ only)

**Reproduce locally:**
```bash
ruff check --no-fix .
ruff format --check .
pydocstyle src/
```

**Fix issues:**
```bash
ruff check .  # Auto-fixes where possible
ruff format .  # Auto-formats code
# Fix docstring issues manually per pydocstyle output
```

---

### 2. Type Check Gate

**Tool:** `mypy`  
**Enforcement:** Fail on any type errors  
**Configuration:** `pyproject.toml` `[tool.mypy]` section

**What it enforces:**
- Type annotations are correct
- No untyped function definitions
- No implicit optional types
- Strict equality checks

**Reproduce locally:**
```bash
mypy src/
```

**Coverage:** All library code in `src/` must be type-annotated. Test code and tools are excluded.

---

### 3. Test & Coverage Gate

**Tool:** `pytest` + `coverage`  
**Enforcement:** 
- All tests must pass
- Coverage must be ≥ 85% (lines and branches)
- Coverage measured only on `src/` (library code)

**Configuration:** 
- `pyproject.toml` `[tool.coverage.run]` and `[tool.coverage.report]` sections
- `pyproject.toml` `[tool.pytest.ini_options]` section

**What it enforces:**
- All unit tests pass
- Integration tests pass (when enabled)
- Coverage threshold maintained
- No coverage regression

**Reproduce locally:**
```bash
pytest --cov=src --cov-report=xml --cov-report=term-missing
coverage report --fail-under=85
```

**Coverage scope:**
- **Included:** All code in `src/ezra/` (library code)
- **Excluded:** Test code (`tests/`), tools (`src/ezra/tools/`), `__init__.py` files

**Artifacts:**
- `coverage.xml` — Machine-readable coverage report (uploaded as CI artifact)

---

### 4. Complexity Gate

**Tool:** `radon`  
**Enforcement:** Fail if any function/class has complexity grade worse than C  
**Threshold:** Grade C is the minimum acceptable (D and E are failures)

**What it enforces:**
- Cyclomatic complexity analysis
- Identifies overly complex functions/classes
- Prevents code complexity from growing unbounded

**Reproduce locally:**
```bash
radon cc -s -n C src/ > radon.txt
radon cc -j src/ > radon.json
```

**Grade scale:**
- **A** — Excellent (1-5 complexity)
- **B** — Good (6-10 complexity)
- **C** — Acceptable (11-20 complexity) ← **Minimum threshold**
- **D** — Poor (21-30 complexity) ← **Fails CI**
- **E** — Very poor (31+ complexity) ← **Fails CI**

**Artifacts:**
- `radon.json` — Machine-readable complexity report (uploaded as CI artifact)
- `radon.txt` — Human-readable complexity report (uploaded as CI artifact)

---

### 5. Security Gate

**Tools:** `bandit`, `pip-audit`, `gitleaks`  
**Enforcement:** Fail on HIGH severity issues

#### 5.1 Bandit (Static Security Analysis)

**Tool:** `bandit`  
**Enforcement:** Fail on HIGH severity security issues  
**Scope:** All code in `src/`

**What it enforces:**
- Detects common security vulnerabilities (SQL injection, hardcoded secrets, etc.)
- Identifies insecure coding patterns
- Flags use of dangerous functions

**Reproduce locally:**
```bash
bandit -r src/ --severity-level high
bandit -r src/ -f json -o bandit.json
```

**Artifacts:**
- `bandit.json` — Machine-readable security scan report (uploaded as CI artifact)

#### 5.2 pip-audit (Dependency Vulnerability Scanning)

**Tool:** `pip-audit`  
**Enforcement:** Fail on any known vulnerabilities in dependencies  
**Scope:** All installed dependencies (including transitive)

**What it enforces:**
- Scans installed packages against vulnerability databases
- Identifies known CVEs in dependencies
- Enforces dependency hygiene

**Reproduce locally:**
```bash
pip-audit --desc
pip-audit --format json --output pip_audit.json --desc
```

**Artifacts:**
- `pip_audit.json` — Machine-readable vulnerability report (uploaded as CI artifact)

#### 5.3 Gitleaks (Secret Detection)

**Tool:** `gitleaks` (via GitHub Action)  
**Enforcement:** Fail on any detected secrets in repository  
**Scope:** Entire repository history

**What it enforces:**
- Detects hardcoded secrets (API keys, passwords, tokens, etc.)
- Scans commit history for leaked credentials
- Prevents secret exposure in version control

**Reproduce locally:**
```bash
# Install gitleaks (see https://github.com/gitleaks/gitleaks)
gitleaks detect --verbose --report-format json --report-path gitleaks.json
```

**Artifacts:**
- `gitleaks.json` — Machine-readable secret detection report (uploaded as CI artifact)

---

### 6. SBOM Gate

**Tool:** `cyclonedx-py`  
**Enforcement:** Generate SBOM (does not block build)  
**Format:** CycloneDX JSON v1.4+

**What it enforces:**
- Generates Software Bill of Materials (SBOM)
- Lists all dependencies with versions
- Enables supply chain transparency

**Reproduce locally:**
```bash
cyclonedx-py -o sbom.cdx.json -e
```

**Artifacts:**
- `sbom.cdx.json` — CycloneDX JSON SBOM (uploaded as CI artifact, 90-day retention)

**Note:** SBOM generation does not block the build. Failures are logged but do not cause CI to fail.

---

### 7. Determinism Gate

**Tool:** Custom script (`scripts/check_determinism.py`)  
**Enforcement:** Fail if EPB bundles are not byte-identical across N≥3 runs

**What it enforces:**
- EPB bundle emission is deterministic
- No non-deterministic behavior in core emission logic
- Timestamp injection does not break determinism
- Hash integrity preserved across runs

**Reproduce locally:**
```bash
python scripts/check_determinism.py --output-dir determinism_output --runs 3
```

**Artifacts:**
- `determinism_output/bundle_run_1/` — First run EPB bundle
- `determinism_output/bundle_run_2/` — Second run EPB bundle
- `determinism_output/bundle_run_3/` — Third run EPB bundle
- `determinism_output/determinism_report.json` — Determinism verification report

**Verification:** All files in `bundle_run_1`, `bundle_run_2`, and `bundle_run_3` must be byte-identical (modulo timestamp fields in manifest.json).

---

## Compliance Framework Mapping

EZRA's quality gates align with the following enterprise governance frameworks:

### NIST Secure Software Development Framework (SSDF)

| SSDF Practice | EZRA Gate | Evidence |
|--------------|-----------|----------|
| PO.3.1 — Protect all forms of code from unauthorized access | Gitleaks | Secret detection in CI |
| PO.3.2 — Maintain provenance data | SBOM | CycloneDX SBOM generation |
| PS.1.1 — Create source code by adhering to secure coding practices | Bandit | Static security analysis |
| PS.3.1 — Create and maintain provenance information | SBOM | SBOM artifact |
| PW.7.1 — Verify that vulnerabilities are addressed | pip-audit | Dependency vulnerability scanning |
| PW.7.2 — Verify that code does not contain malicious functionality | Bandit + Gitleaks | Security scanning |
| PW.8.1 — Verify that code is traceable | Coverage | Test coverage ≥ 85% |
| PW.8.2 — Verify that code is maintainable | Complexity | Radon complexity gate (grade C) |
| RV.1.1 — Identify and confirm vulnerabilities | pip-audit + Bandit | Vulnerability scanning |
| RV.1.2 — Assess and prioritize vulnerabilities | Bandit severity levels | HIGH severity enforcement |

### OWASP Application Security Verification Standard (ASVS) Level 2

| ASVS Requirement | EZRA Gate | Evidence |
|------------------|-----------|----------|
| V1.1.1 — Verify use of up-to-date and trusted components | pip-audit | Dependency vulnerability scanning |
| V1.2.1 — Verify that all components are inventory | SBOM | CycloneDX SBOM |
| V1.2.2 — Verify that all components are analyzed for vulnerabilities | pip-audit | Dependency scanning |
| V7.1.1 — Verify that all code is maintained | Coverage | Test coverage ≥ 85% |
| V7.2.1 — Verify that code complexity is managed | Complexity | Radon complexity gate |
| V14.2.1 — Verify that secrets are not hardcoded | Gitleaks | Secret detection |

### OpenSSF Scorecard

| Scorecard Check | EZRA Gate | Evidence |
|-----------------|-----------|----------|
| Security-Policy | Security Gate | Bandit, pip-audit, gitleaks |
| Dependency-Update-Tool | pip-audit | Dependency vulnerability scanning |
| Code-Review | Lint + Type Check | Automated code quality checks |
| Maintained | Coverage + Complexity | Test coverage and complexity gates |
| Signed-Releases | SBOM | CycloneDX SBOM generation |

### 8. Dependency Review Gate

**Tool:** `actions/dependency-review-action@v4`  
**Enforcement:** Fail on moderate+ severity vulnerabilities in dependency changes  
**Scope:** Pull requests only (compares base vs head dependencies)

**What it enforces:**
- Detects new vulnerabilities introduced by dependency changes
- Reviews dependency additions/updates for security issues
- Blocks PRs with moderate+ severity vulnerabilities

**Reproduce locally:**
```bash
# Dependency review runs automatically on PRs
# To check locally, review dependency changes manually
pip-audit --desc  # Check current dependencies
```

**Note:** This gate only runs on `pull_request` events, not on `push` to main.

---

### 9. OpenSSF Scorecard Gate (Informational)

**Tool:** `ossf/scorecard-action@v2`  
**Enforcement:** Warn-first (non-blocking, `continue-on-error: true`)  
**Scope:** All CI runs

**What it enforces:**
- Automated security posture assessment
- Checks security policy, dependency updates, code review practices, etc.
- Uploads SARIF results to GitHub Security tab

**Reproduce locally:**
```bash
# Install scorecard CLI (see https://github.com/ossf/scorecard)
scorecard --repo=https://github.com/OWNER/REPO
```

**Note:** This check is **informational and non-blocking**. It does not block merges but provides security posture insights.

**Artifacts:**
- `scorecard-results.sarif` — Scorecard results in SARIF format (uploaded to Security tab and as artifact)

---

### 10. SLSA Provenance Gate

**Tool:** `actions/attest-build-provenance@v1`  
**Enforcement:** Generate build attestations  
**Scope:** `push` to `main` and tags only

**What it enforces:**
- Build attestation generation for supply chain integrity
- Provenance metadata for package builds
- SLSA Level 1+ compliance

**Reproduce locally:**
```bash
# Build package
python -m build

# Attestation is generated automatically in CI on main/tags
```

**Note:** This gate only runs on `push` to `main` and tag events. It requires `id-token: write` permission (job-level).

**Artifacts:**
- Build artifacts (`dist/*.whl`, `dist/*.tar.gz`) — Uploaded as provenance artifacts
- SLSA attestations — Generated and stored in GitHub attestations

---

## Local Development Workflow

### Running All Quality Checks Locally

```bash
# 1. Install dependencies
pip install -e ".[dev]"

# 2. Lint
ruff check .
ruff format .

# 3. Type check
mypy src/

# 4. Tests and coverage
pytest --cov=src --cov-report=xml --cov-report=term-missing
coverage report --fail-under=85

# 5. Complexity
radon cc -s -n C src/ > radon.txt
radon cc -j src/ > radon.json

# 6. Security
bandit -r src/ --severity-level high
bandit -r src/ -f json -o bandit.json
pip-audit --desc
pip-audit --format json --output pip_audit.json --desc

# 7. SBOM
cyclonedx-py -o sbom.cdx.json -e

# 8. Determinism
python scripts/check_determinism.py --output-dir determinism_output --runs 3
```

### Pre-Commit Checklist

Before committing, ensure:

- [ ] `ruff check .` passes
- [ ] `ruff format .` applied
- [ ] `mypy src/` passes
- [ ] `pytest` passes with coverage ≥ 85%
- [ ] `radon cc -s -n C src/` shows no grades worse than C
- [ ] `bandit -r src/ --severity-level high` passes
- [ ] `pip-audit --desc` shows no vulnerabilities
- [ ] No secrets detected (manual review or gitleaks)

---

## CI Artifact Retention

| Artifact | Retention | Purpose |
|----------|-----------|---------|
| `coverage.xml` | 30 days | Coverage evidence |
| `radon.json`, `radon.txt` | 30 days | Complexity evidence |
| `bandit.json` | 30 days | Security scan evidence |
| `pip_audit.json` | 30 days | Vulnerability evidence |
| `gitleaks.json` | 30 days | Secret detection evidence |
| `sbom.cdx.json` | 90 days | Supply chain evidence |
| `determinism-artifacts` | 7 days | Determinism verification |

---

## Quality Gate Evolution

Quality gates are **invariants** and must not be weakened without milestone-level justification.

**Current thresholds:**
- Coverage: ≥ 85% (lines and branches)
- Complexity: Grade C minimum (fail on D/E)
- Security: Fail on HIGH severity issues
- Determinism: Byte-identical across N≥3 runs

**Change process:**
Any threshold change requires:
1. New milestone
2. Explicit audit justification
3. Evidence of no behavioral regression
4. Update to this document

---

## References

- [NIST SSDF](https://csrc.nist.gov/publications/detail/sp/800-218/final)
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
- [OpenSSF Scorecard](https://securityscorecards.dev/)
- [SLSA Framework](https://slsa.dev/)
- [CycloneDX Specification](https://cyclonedx.org/specification/overview/)

---

**Last Updated:** M15 (2026-02-26)  
**Maintainer:** EZRA Governance

