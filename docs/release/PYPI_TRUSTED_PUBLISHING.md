# PyPI Trusted Publishing for EZRA

This document describes how to configure PyPI so that the EZRA release workflow (`.github/workflows/release.yml`) can publish packages using **Trusted Publishing** (OIDC). No API tokens are stored in the repository or GitHub secrets.

---

## Prerequisites

- You have maintainer or owner access to the [ezra](https://pypi.org/project/ezra/) project on PyPI (or will create the project).
- The EZRA source repository is on GitHub.

---

## 1. Create the PyPI project (if it does not exist)

1. Log in to [PyPI](https://pypi.org/).
2. Go to **Your projects** → **Add new project**.
3. Create a project with the exact name: **`ezra`** (must match `pyproject.toml` and the release workflow).

---

## 2. Enable Trusted Publishing on PyPI

1. Open the **ezra** project on PyPI.
2. Go to **Publishing** (or **Manage** → **Publishing**).
3. Under **Add a new pending publisher**, configure:
   - **PyPI Project Name:** `ezra`
   - **Owner:** your GitHub org or username (e.g. `your-org` or `your-username`)
   - **Repository name:** `ezra` (or the actual repo name)
   - **Workflow name:** `release.yml`
   - **Environment name (optional):** `pypi` (must match the `environment.name` in `.github/workflows/release.yml`)

4. Click **Add** so the publisher is in a pending state.

---

## 3. Add GitHub as a trusted source

1. In the same **Publishing** section, ensure the pending publisher shows:
   - **Owner / Repository:** `owner/repo`
   - **Workflow:** `release.yml`
   - **Environment:** `pypi`

2. PyPI will display the **Trusted Publisher** details. No further PyPI-side steps are required once the publisher is added and approved (if your PyPI account has permission to approve it).

---

## 4. Configure the GitHub environment (recommended)

1. In the EZRA GitHub repo: **Settings** → **Environments**.
2. Create an environment named **`pypi`** (same as in the workflow).
3. (Optional) Add **Environment protection rules** (e.g. require a reviewer) if you want to gate releases.
4. The release workflow uses `environment: pypi` so that only runs targeting this environment can obtain the OIDC token that PyPI accepts.

---

## 5. Triggering a release

After the above is configured:

```bash
git tag v1.0.1
git push --tags
```

The **Release** workflow runs on tag push, builds the sdist and wheel, generates hashes and SBOM, and the **Publish to PyPI** job publishes to PyPI using OIDC. No `TWINE_USERNAME` / `TWINE_PASSWORD` or API token is required.

---

## 6. Verifying

- On PyPI, the **ezra** project will show the new version and files after a successful run.
- In GitHub Actions, the **Release** workflow run will show the **Publish to PyPI** job as successful when Trusted Publishing is correctly set up.

If the publish step fails with an authentication or permissions error, re-check:

- PyPI project name is exactly **ezra**.
- Owner and repository name on PyPI match the GitHub repo.
- Workflow name is **release.yml** and environment name is **pypi**.
- The **pypi** environment exists in GitHub (Settings → Environments).
