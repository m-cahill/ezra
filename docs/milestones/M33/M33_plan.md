# M33 — Reproducible Distribution Artifacts & Trusted Publishing

**Phase:** XVIII — Distribution & Supply Chain Hardening
**Version Target:** v1.0.x (no runtime changes)
**Type:** Packaging + Supply Chain Hardening
**Scope:** EZRA repo only

**No runtime or EPB changes allowed**

---

# 1. Intent

M32 established deterministic dependency resolution and CI immutability through lockfiles and pinned actions.

M33 extends that work to **distribution artifacts**.

The goal is to ensure that:

```
source commit
      ↓
sdist
      ↓
wheel
```

produces **verifiable, deterministic artifacts** with **cryptographic provenance**.

This milestone introduces:

* reproducible `sdist` and `wheel`
* artifact hashing
* build verification
* PyPI Trusted Publishing
* release artifact provenance

The result is that **EZRA distributions become verifiable supply-chain artifacts**, not just repository code.

---

# 2. Hard Invariants (Non-Negotiable)

The following must NOT change:

* EPB schema
* Canonicalization logic
* Hashing logic
* Signing logic
* Plugin interfaces
* Zone registry format
* CI enforcement thresholds
* Coverage threshold (85%)
* Determinism checks
* Hermetic reproducibility logic

No runtime logic changes allowed.

---

# 3. Scope

## 3.1 Deterministic Build Artifacts

Add deterministic packaging for:

```
sdist
wheel
```

Implementation:

```
python -m build
```

CI must generate both artifacts.

Acceptance Criteria:

* `dist/*.tar.gz`
* `dist/*.whl`

Artifacts generated in CI match local build structure.

---

## 3.2 Artifact Hash Verification

Generate SHA256 hashes for build artifacts.

Example:

```
sha256sum dist/*
```

CI must verify:

```
local build hash == CI build hash
```

Artifacts must be deterministic across environments.

Acceptance Criteria:

* identical hash from local build and CI build
* artifact hash logged in CI output

---

## 3.3 PyPI Trusted Publishing

Configure GitHub → PyPI trusted publishing.

Requirements:

* No API tokens committed
* OIDC trusted publishing enabled
* Release workflow triggers on tag

Workflow example:

```
push:
  tags:
    - v*
```

Acceptance Criteria:

* GitHub Actions publishes release to PyPI
* PyPI verifies OIDC identity
* No secrets required

---

## 3.4 Release Artifact Provenance

Enable provenance attestation.

Use:

```
actions/attest-build-provenance
```

Artifacts must include:

* provenance attestation
* SBOM
* artifact hashes

Acceptance Criteria:

* CI publishes attestations
* provenance tied to build commit

---

## 3.5 Release Workflow

Introduce release workflow:

```
.github/workflows/release.yml
```

Steps:

1. checkout repo
2. install dependencies
3. build artifacts
4. generate hashes
5. verify determinism
6. generate SBOM
7. publish artifacts
8. publish provenance

Acceptance Criteria:

* workflow runs on tag
* artifacts reproducible
* release automated

---

# 4. Out of Scope

The following remain out of scope:

* No runtime refactors
* No EPB changes
* No RediAI integration
* No performance work
* No architecture changes
* No dependency changes
* No CI threshold changes
* No feature development

This milestone strictly concerns **distribution artifacts**.

---

# 5. Verification Plan

Verification sequence:

### Local verification

```
git clone
pip install -r requirements.txt
python -m build
```

Confirm artifacts produced.

---

### Deterministic artifact check

Run build twice:

```
python -m build
rm dist/*
python -m build
```

Hashes must match.

---

### CI verification

CI must confirm:

* build reproducible
* artifact hashes identical
* provenance generated
* SBOM generated

---

# 6. Acceptance Criteria

M33 is complete when:

* deterministic `sdist` generated
* deterministic `wheel` generated
* artifact hashes verified
* Trusted Publishing configured
* release workflow implemented
* provenance attestation generated
* SBOM attached to release
* CI passes with no threshold weakening
* no runtime or EPB changes

---

# 7. Risk Assessment

Risk: **Low**

Blast Radius:

```
packaging
release workflow
distribution pipeline
```

Rollback:

```
revert release workflow PR
```

No runtime impact.

---

# 8. Deliverables

Artifacts introduced:

```
.github/workflows/release.yml
dist/*.whl
dist/*.tar.gz
artifact hashes
provenance attestations
```

Milestone documents:

```
docs/milestones/M33/M33_plan.md
docs/milestones/M33/M33_run1.md
docs/milestones/M33/M33_audit.md
docs/milestones/M33/M33_summary.md
docs/milestones/M33/M33_toolcalls.md
```

---

# 9. Definition of Done

M33 is complete when:

* EZRA can be built deterministically from source
* artifacts reproducible across environments
* PyPI publishing automated
* build provenance attached
* SBOM attached
* CI green
* all invariants preserved

---

# 10. Expected Governance Outcome

After M33, EZRA will have:

| Property                       | Status |
| ------------------------------ | ------ |
| Deterministic dependency graph | ✔      |
| Immutable CI                   | ✔      |
| Reproducible build artifacts   | ✔      |
| Artifact hashing               | ✔      |
| Trusted PyPI publishing        | ✔      |
| Provenance attestation         | ✔      |
| SBOM generation                | ✔      |

This milestone moves EZRA from:

```
reproducible repository
```

to

```
verifiable distribution artifact
```

---

# Cursor Implementation Notes

Cursor should:

1. Implement deterministic build pipeline.
2. Add release workflow.
3. Verify artifact hashes.
4. Configure trusted publishing.
5. Preserve all invariants.
6. Produce milestone artifacts.
7. Keep CI green.

No runtime modifications allowed.

---
