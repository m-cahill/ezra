# EZRA

Extensible Zone-Based Runtime Architecture.

EZRA is a modular runtime perception engine that converts raw screen pixels into structured, interpretable state for interactive systems.

## Scope

- Runtime inference only
- Plugin-first architecture
- ML models are external artifacts
- No training logic

See: [docs/VISION.md](docs/VISION.md)

## Releases

Releases are produced using deterministic builds and GitHub Trusted Publishing.

Tagging `v*` triggers the release pipeline which produces:

- reproducible sdist + wheel
- artifact hashes
- CycloneDX SBOM
- SLSA provenance

See [docs/release/PYPI_TRUSTED_PUBLISHING.md](docs/release/PYPI_TRUSTED_PUBLISHING.md).

