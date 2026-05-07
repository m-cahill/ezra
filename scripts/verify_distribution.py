#!/usr/bin/env python3
"""Verify EZRA distribution artifacts for a tag are reproducible and valid.

Two modes:

* **release** (default): Downloads release artifacts from GitHub Actions for the
  given tag, rebuilds locally, and validates hashes, SBOM, and provenance.
* **ci-local**: Runs one local ``python -m build``, writes ``SHA256SUMS.txt`` from
  the produced wheel/sdist, verifies hashes against that file, generates a local
  CycloneDX SBOM, and validates SBOM shape. Does not call the GitHub API (no token).

Usage:
    python scripts/verify_distribution.py --tag v1.0.1-m33
    python scripts/verify_distribution.py --tag latest
    python scripts/verify_distribution.py --mode ci-local

Exit codes:
    0: Distribution verified
    1: Verification failed
    2: Error (e.g. missing token, run not found)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

RELEASE_WORKFLOW_PATH = ".github/workflows/release.yml"
REQUIRED_ARTIFACTS = ("ezra-distribution", "ezra-sbom", "ezra-provenance")
SHA256SUMS_FILENAME = "SHA256SUMS.txt"
SBOM_FILENAME = "sbom.json"
PROVENANCE_FILENAME = "provenance.json"


def _clean_dist_dir(dist_dir: Path) -> None:
    """Remove all files and subdirs under dist/."""
    if not dist_dir.is_dir():
        return
    for p in dist_dir.iterdir():
        if p.is_file():
            p.unlink()
        elif p.is_dir():
            shutil.rmtree(p)


def _hash_dist_artifacts(dist_dir: Path) -> dict[str, str]:
    """SHA256 hex (lower) for each file in dist except SHA256SUMS.txt."""
    out: dict[str, str] = {}
    if not dist_dir.is_dir():
        return out
    for f in sorted(dist_dir.iterdir()):
        if f.is_file() and f.name != SHA256SUMS_FILENAME:
            out[f.name] = hashlib.sha256(f.read_bytes()).hexdigest().lower()
    return out


def _write_sha256sums(dist_dir: Path, file_hashes: dict[str, str]) -> None:
    """Write dist/SHA256SUMS.txt in the same format as the release workflow."""
    lines = [f"{h}  {name}\n" for name, h in sorted(file_hashes.items())]
    (dist_dir / SHA256SUMS_FILENAME).write_text("".join(lines), encoding="utf-8")


def _run_build(repo_root: Path) -> None:
    """Run python -m build; raises on failure."""
    env = os.environ.copy()
    # Deterministic sdist/wheel metadata for reproducibility checks (CI + ci-local).
    env.setdefault("SOURCE_DATE_EPOCH", "1704067200")
    subprocess.run(
        [sys.executable, "-m", "build"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        env=env,
    )


def _run_cyclonedx_sbom(repo_root: Path, dest: Path) -> None:
    """Generate CycloneDX JSON via cyclonedx-py (matches CI SBOM job)."""
    exe = shutil.which("cyclonedx-py")
    cmd = (
        [exe, "environment", "-o", str(dest)]
        if exe
        else [sys.executable, "-m", "cyclonedx_py", "environment", "-o", str(dest)]
    )
    subprocess.run(
        cmd,
        cwd=repo_root,
        check=True,
        capture_output=True,
    )


def run_ci_local(repo_root: Path) -> dict[str, object]:
    """PR/main-safe verification: one reproducible build, hash consistency, SBOM check."""
    dist_dir = repo_root / "dist"
    _clean_dist_dir(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)

    _run_build(repo_root)
    hashes = _hash_dist_artifacts(dist_dir)
    has_whl = any(n.endswith(".whl") for n in hashes)
    has_sdist = any(n.endswith(".tar.gz") for n in hashes)
    if not has_whl or not has_sdist:
        raise RuntimeError("ci-local: expected wheel and sdist in dist/ after build")
    _write_sha256sums(dist_dir, hashes)
    artifact_ok = _verify_artifact_hashes(dist_dir)

    sbom_path = dist_dir / SBOM_FILENAME
    _run_cyclonedx_sbom(repo_root, sbom_path)
    sbom_ok = _validate_sbom(sbom_path)

    ci_note = (
        "PR/main mode: local build + SHA256SUMS self-check + SBOM; no GitHub artifact download"
    )
    prov_note = "ci-local does not validate release provenance.json (use --mode release)"
    return {
        "artifact_hashes_match": artifact_ok,
        "ci_local_note": ci_note,
        "mode": "ci-local",
        "provenance_checked": False,
        "provenance_note": prov_note,
        "sbom_valid": sbom_ok,
        "distribution_verified": bool(artifact_ok and sbom_ok),
    }


def _gh_api(
    method: str,
    path: str,
    token: str,
    *,
    parse: bool = True,
) -> Any:
    """Call GitHub REST API; path is e.g. /repos/owner/repo/..."""
    url = f"https://api.github.com{path}"
    req = Request(url, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    with urlopen(req) as resp:
        data = resp.read().decode()
    return json.loads(data) if parse else None


def _get_workflow_id(owner: str, repo: str, token: str) -> int | None:
    """Return workflow ID for release.yml."""
    data = _gh_api("GET", f"/repos/{owner}/{repo}/actions/workflows", token)
    if not isinstance(data, dict):
        return None
    for w in data.get("workflows", []):
        if not isinstance(w, dict):
            continue
        path = w.get("path") or ""
        if path == RELEASE_WORKFLOW_PATH or path.endswith("release.yml"):
            wid = w.get("id")
            return int(wid) if isinstance(wid, int) else None
    return None


def _get_tag_sha(owner: str, repo: str, tag: str, token: str) -> str | None:
    """Return commit SHA for tag (refs/tags/TAG)."""
    ref = f"tags/{tag}" if not tag.startswith("refs/") else tag.replace("refs/", "")
    try:
        data = _gh_api("GET", f"/repos/{owner}/{repo}/git/ref/{ref}", token)
        if not isinstance(data, dict):
            return None
        obj = data.get("object")
        if not isinstance(obj, dict):
            return None
        sha = obj.get("sha")
        if isinstance(sha, str) and obj.get("type") == "tag":
            tag_data = _gh_api("GET", f"/repos/{owner}/{repo}/git/tags/{sha}", token)
            if isinstance(tag_data, dict):
                obj2 = tag_data.get("object")
                if isinstance(obj2, dict):
                    sha = obj2.get("sha")
        return str(sha) if isinstance(sha, str) else None
    except Exception:
        return None


def _resolve_latest_tag(owner: str, repo: str, token: str) -> str | None:
    """Return the latest tag name by workflow run order (most recent release)."""
    wf_id = _get_workflow_id(owner, repo, token)
    if not wf_id:
        return None
    data = _gh_api(
        "GET",
        f"/repos/{owner}/{repo}/actions/workflows/{wf_id}/runs?per_page=1",
        token,
    )
    if not isinstance(data, dict):
        return None
    runs = data.get("workflow_runs") or []
    if not isinstance(runs, list) or not runs:
        return None
    run = runs[0]
    if not isinstance(run, dict):
        return None
    ref = run.get("head_branch") or ""
    if ref.startswith("v") and run.get("event") == "push":
        return ref
    head_sha = run.get("head_sha")
    tags_data = _gh_api("GET", f"/repos/{owner}/{repo}/tags?per_page=100", token)
    if isinstance(tags_data, list):
        for t in tags_data:
            if isinstance(t, dict):
                c = t.get("commit")
                if isinstance(c, dict) and c.get("sha") == head_sha:
                    name = t.get("name")
                    return str(name) if isinstance(name, str) else None
    return None


def _get_run_id_for_tag(
    owner: str,
    repo: str,
    tag: str,
    token: str,
) -> int | None:
    """Return the workflow run ID for the release triggered by this tag."""
    wf_id = _get_workflow_id(owner, repo, token)
    if not wf_id:
        return None
    tag_sha = _get_tag_sha(owner, repo, tag, token)
    if not tag_sha:
        return None
    data = _gh_api(
        "GET",
        f"/repos/{owner}/{repo}/actions/workflows/{wf_id}/runs?per_page=20",
        token,
    )
    if not isinstance(data, dict):
        return None
    for run in data.get("workflow_runs", []):
        if (
            isinstance(run, dict)
            and run.get("head_sha") == tag_sha
            and run.get("status") == "completed"
        ):
            rid = run.get("id")
            return int(rid) if isinstance(rid, int) else None
    return None


def _download_artifact_zip(
    owner: str,
    repo: str,
    artifact_id: int,
    token: str,
    dest_dir: Path,
) -> None:
    """Download artifact by ID (zip) and extract into dest_dir."""
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip"
    req = Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    with urlopen(req) as resp:
        zip_path = dest_dir / "artifact.zip"
        zip_path.write_bytes(resp.read())
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dest_dir)
    zip_path.unlink()


def _download_artifacts(
    owner: str,
    repo: str,
    run_id: int,
    token: str,
    work_dir: Path,
) -> dict[str, Path]:
    """Download required artifacts for the run; return paths to each artifact dir/file."""
    data = _gh_api(
        "GET",
        f"/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts",
        token,
    )
    if not isinstance(data, dict):
        raise RuntimeError("Failed to list artifacts")
    artifacts = {
        a["name"]: a
        for a in data.get("artifacts", [])
        if isinstance(a, dict) and "name" in a and "id" in a
    }
    result: dict[str, Path] = {}
    for name in REQUIRED_ARTIFACTS:
        if name not in artifacts:
            raise RuntimeError(f"Missing artifact: {name}")
        aid = artifacts[name]["id"]
        adir = work_dir / name
        adir.mkdir(parents=True, exist_ok=True)
        _download_artifact_zip(owner, repo, aid, token, adir)
        if name == "ezra-sbom":
            result[name] = adir / SBOM_FILENAME
        elif name == "ezra-provenance":
            result[name] = adir / PROVENANCE_FILENAME
        else:
            result[name] = adir
    return result


def _parse_sha256sums(path: Path) -> dict[str, str]:
    """Parse SHA256SUMS.txt; return dict of filename -> hash."""
    out: dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) == 2:
            out[parts[1]] = parts[0].lower()
    return out


def _verify_artifact_hashes(artifact_dir: Path) -> bool:
    """Verify dist files match SHA256SUMS.txt. Returns True if match."""
    sums_path = artifact_dir / SHA256SUMS_FILENAME
    if not sums_path.exists():
        return False
    expected = _parse_sha256sums(sums_path)
    for name, exp_hash in expected.items():
        if name == SHA256SUMS_FILENAME:
            continue
        fp = artifact_dir / name
        if not fp.is_file():
            return False
        h = hashlib.sha256(fp.read_bytes()).hexdigest().lower()
        if h != exp_hash:
            return False
    return True


def _rebuild_and_compare(repo_root: Path, release_hashes: dict[str, str]) -> bool:
    """Run python -m build and compare hashes. Returns True if identical."""
    dist_dir = repo_root / "dist"
    dist_dir.mkdir(exist_ok=True)
    subprocess.run(
        [sys.executable, "-m", "build"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    local_hashes: dict[str, str] = {}
    for f in dist_dir.iterdir():
        if f.is_file() and f.name != SHA256SUMS_FILENAME:
            local_hashes[f.name] = hashlib.sha256(f.read_bytes()).hexdigest().lower()
    for name, exp_hash in release_hashes.items():
        if name == SHA256SUMS_FILENAME:
            continue
        if local_hashes.get(name) != exp_hash.lower():
            return False
    return True


def _validate_sbom(path: Path) -> bool:
    """Validate SBOM: valid JSON, non-empty components/dependencies, schema present."""
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return False
    if not isinstance(data, dict):
        return False
    # CycloneDX has components or dependencies
    components = data.get("components", [])
    if not components and "dependencies" not in data:
        return False
    return True


def _validate_provenance(path: Path) -> bool:
    """Validate provenance: commit, builder, workflow, artifact_hashes present."""
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return False
    if not isinstance(data, dict):
        return False
    required = ("commit", "builder", "workflow", "artifact_hashes")
    return all(k in data for k in required)


def main() -> int:
    """Run distribution verification and print report."""
    parser = argparse.ArgumentParser(description="Verify EZRA distribution for a tag.")
    parser.add_argument(
        "--mode",
        choices=("release", "ci-local"),
        default="release",
        help="release: download GitHub release artifacts; ci-local: local build + SBOM (PR/main)",
    )
    parser.add_argument(
        "--tag",
        default="latest",
        help="Tag to verify (e.g. v1.0.1-m33) or 'latest' (release mode only)",
    )
    parser.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY", ""),
        help="GitHub repo owner/name (default: GITHUB_REPOSITORY; release mode only)",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("GITHUB_TOKEN", ""),
        help="GitHub token (default: GITHUB_TOKEN; release mode only)",
    )
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parent.parent

    if args.mode == "ci-local":
        try:
            report = run_ci_local(repo_root)
        except (OSError, subprocess.CalledProcessError, RuntimeError) as e:
            print(f"error: ci-local verification failed: {e}", file=sys.stderr)
            return 2
        print(json.dumps(report, sort_keys=True, indent=2))
        return 0 if report.get("distribution_verified") else 1

    if not args.repo or "/" not in args.repo:
        print("error: --repo or GITHUB_REPOSITORY required (owner/repo)", file=sys.stderr)
        return 2
    if not args.token:
        print("error: --token or GITHUB_TOKEN required", file=sys.stderr)
        return 2

    owner, repo = args.repo.split("/", 1)
    tag = args.tag
    if tag == "latest":
        tag = _resolve_latest_tag(owner, repo, args.token)
        if not tag:
            print("error: could not resolve latest tag", file=sys.stderr)
            return 2

    run_id = _get_run_id_for_tag(owner, repo, tag, args.token)
    if not run_id:
        print(f"error: no completed release run found for tag {tag}", file=sys.stderr)
        return 2

    report: dict[str, object] = {
        "artifact_hashes_match": False,
        "distribution_verified": False,
        "mode": "release",
        "provenance_valid": False,
        "rebuild_hash_match": False,
        "sbom_valid": False,
        "tag": tag,
    }

    with tempfile.TemporaryDirectory() as work_dir:
        work = Path(work_dir)
        paths = _download_artifacts(owner, repo, run_id, args.token, work)

        dist_path = paths["ezra-distribution"]
        report["artifact_hashes_match"] = _verify_artifact_hashes(dist_path)
        release_hashes = _parse_sha256sums(dist_path / SHA256SUMS_FILENAME)

        report["sbom_valid"] = _validate_sbom(paths["ezra-sbom"])
        report["provenance_valid"] = _validate_provenance(paths["ezra-provenance"])

        report["rebuild_hash_match"] = _rebuild_and_compare(repo_root, release_hashes)

    report["distribution_verified"] = (
        report["artifact_hashes_match"]
        and report["rebuild_hash_match"]
        and report["sbom_valid"]
        and report["provenance_valid"]
    )

    print(json.dumps(report, sort_keys=True, indent=2))
    return 0 if report["distribution_verified"] else 1


if __name__ == "__main__":
    sys.exit(main())
