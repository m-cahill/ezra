# EZRA

Extensible Zone-Based Runtime Architecture.

EZRA is a modular runtime perception engine that converts raw screen pixels into structured, interpretable state for interactive systems.

## Scope

- Runtime inference only
- Plugin-first architecture
- ML models are external artifacts
- No training logic

See: [docs/VISION.md](docs/VISION.md)

## Quickstart

Create a virtual environment and install EZRA in editable mode:

```bash
pip install -e ".[dev]"
```

Run the developer checks:

```bash
ruff check .
ruff format --check .
mypy src
pytest
```

Optional plugins may be installed separately (e.g. EasyOCR).

## Architecture

EZRA follows a strict separation of concerns:

- **Core Engine** — runtime perception orchestration
- **Plugins** — model adapters (EasyOCR, Tesseract, etc.)
- **EPB** — deterministic artifact bundle output
- **Zones** — structured state projections
- **EPB Tools** — certification, signing, verification

The core runtime is intentionally **ML-free**; models remain external artifacts.

See: [docs/VISION.md](docs/VISION.md) · [docs/ezra.md](docs/ezra.md)

## Development Workflow

CI enforces:

- Ruff lint and formatting
- MyPy static typing
- pytest with coverage ≥85%
- deterministic EPB bundle generation
- hermetic reproducibility across Python versions
- security scans (Bandit, pip-audit, gitleaks)
- SBOM generation

## Releases

Releases are produced using deterministic builds and GitHub Trusted Publishing.

Tagging `v*` triggers the release pipeline which produces:

- reproducible sdist + wheel
- artifact hashes
- CycloneDX SBOM
- SLSA provenance

See [docs/release/PYPI_TRUSTED_PUBLISHING.md](docs/release/PYPI_TRUSTED_PUBLISHING.md).

## Distribution Verification

To validate that release artifacts are reproducible (same hashes as the release workflow):

```bash
python scripts/verify_distribution.py --tag latest
```

Or for a specific tag (e.g. `v1.0.1-m33`):

```bash
python scripts/verify_distribution.py --tag v1.0.1-m33
```

Requires `GITHUB_TOKEN` and `GITHUB_REPOSITORY` (or `--repo owner/name`). See [docs/release/DISTRIBUTION_VERIFICATION.md](docs/release/DISTRIBUTION_VERIFICATION.md).

