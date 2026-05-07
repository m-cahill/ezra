# EZRA

**Extensible Zone-Based Runtime Architecture**

EZRA is a modular **runtime perception engine**: it turns raw screen pixels into structured, interpretable state for games, UI automation, and research rigs. The core orchestration layer stays **ML-free**; models load through a **plugin** interface.

## What EZRA is

- A **runtime** that runs inference and emits deterministic **EZRA Perception Bundle (EPB)** artifacts
- **Plugin-first** (e.g. OCR backends registered in code, lazy-loaded)
- Focused on **deterministic**, **auditable** output suitable for downstream certification

## What EZRA is not

- **Not a training stack** — training belongs outside EZRA (e.g. RediAI v3 / other pipelines)
- **Not an annotation product** — use external tools; EZRA consumes exported data as needed
- **Not integrated with RediAI at runtime** — consumers validate **EPB bundles** as files; there is no shared runtime or importer coupling

North star and boundaries: **[docs/VISION.md](docs/VISION.md)** · Governance ledger: **[docs/ezra.md](docs/ezra.md)** · Contributor guide: **[CONTRIBUTING.md](CONTRIBUTING.md)**

## Quickstart

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Unix: source .venv/bin/activate

pip install -e ".[dev]"
```

## Verification (local)

```bash
ruff check .
ruff format --check .
mypy src
pytest
```

Optional parity with CI supply-chain and distribution smoke:

```bash
pip-audit -r requirements.txt
python scripts/verify_distribution.py --mode ci-local
```

Integration and parity test suites are opt-in via environment variables — see **[CONTRIBUTING.md](CONTRIBUTING.md)**.

## EPB and RediAI (artifact boundary)

EZRA emits **EPB v1.0.0** bundles (manifest, detections, state, hashes, optional extensions). **RediAI v3** (or any consumer) interacts with EZRA **only by validating those artifacts** — not by importing EZRA at runtime. Specification: **`docs/specs/epb_v1/EPB_V1_SPEC.md`**.

## Security and CI (honest posture)

CI jobs typically include lint, typecheck, tests, coverage, determinism/reproducibility gates, SBOM, and security scans (**Bandit**, **`pip-audit`**, **gitleaks**).

- **Dependency Review** may depend on GitHub Advanced Security / dependency graph; it can be **skipped** in some contexts — that is an infrastructure visibility limit, not a silent waiver of policy.
- **SLSA provenance** — attestation may be **unavailable or conditional** on **private** repositories; workflows are expected to represent that truthfully.

Pre-release verification template: **[docs/release/PUBLIC_RELEASE_CHECKLIST.md](docs/release/PUBLIC_RELEASE_CHECKLIST.md)**

## Releases and PyPI

Tag-driven releases use Trusted Publishing. Details: **[docs/release/PYPI_TRUSTED_PUBLISHING.md](docs/release/PYPI_TRUSTED_PUBLISHING.md)**.

To compare local builds to GitHub-produced artifacts (full verification often uses a **release** mode with a concrete tag — see docs):

```bash
python scripts/verify_distribution.py --tag latest
# or: python scripts/verify_distribution.py --tag v1.0.1-m33
```

See **[docs/release/DISTRIBUTION_VERIFICATION.md](docs/release/DISTRIBUTION_VERIFICATION.md)** for modes, tokens, and limitations.

## Operating manual

AI- and maintainer-oriented runtime reference: **[docs/ezra_operating_manual_v1.md](docs/ezra_operating_manual_v1.md)**
