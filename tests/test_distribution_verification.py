"""Tests for distribution verification script (hash, SBOM, provenance validation)."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

# Load the script module without installing it
SCRIPT_PATH = Path(__file__).resolve().parent.parent / "scripts" / "verify_distribution.py"
spec = importlib.util.spec_from_file_location("verify_distribution", SCRIPT_PATH)
assert spec and spec.loader
verify_distribution = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify_distribution)


def test_parse_sha256sums(tmp_path: Path) -> None:
    """Parse SHA256SUMS.txt returns filename -> hash."""
    sums = tmp_path / "SHA256SUMS.txt"
    sums.write_text(
        "a1b2c3  ezra-1.0.0.tar.gz\nd4e5f6  ezra-1.0.0-py3-none-any.whl\n000000  SHA256SUMS.txt\n"
    )
    result = verify_distribution._parse_sha256sums(sums)
    assert result["ezra-1.0.0.tar.gz"] == "a1b2c3"
    assert result["ezra-1.0.0-py3-none-any.whl"] == "d4e5f6"
    assert result["SHA256SUMS.txt"] == "000000"


def test_parse_sha256sums_empty(tmp_path: Path) -> None:
    """Empty or whitespace-only lines are skipped."""
    sums = tmp_path / "SHA256SUMS.txt"
    sums.write_text("aa  file1\n\n   \nbb  file2\n")
    result = verify_distribution._parse_sha256sums(sums)
    assert result == {"file1": "aa", "file2": "bb"}


def test_verify_artifact_hashes_match(tmp_path: Path) -> None:
    """When file hashes match SHA256SUMS.txt, verification passes."""
    (tmp_path / "ezra-1.0.0.tar.gz").write_bytes(b"content1")
    (tmp_path / "ezra-1.0.0-py3-none-any.whl").write_bytes(b"content2")
    h1 = "5f8e2e4e8e2e4e8e2e4e8e2e4e8e2e4e8e2e4e8e2e4e8e2e4e8e2e4e8e2e4"
    h2 = "6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a"
    # Use actual hashes of the content
    import hashlib

    h1 = hashlib.sha256(b"content1").hexdigest().lower()
    h2 = hashlib.sha256(b"content2").hexdigest().lower()
    (tmp_path / "SHA256SUMS.txt").write_text(
        f"{h1}  ezra-1.0.0.tar.gz\n{h2}  ezra-1.0.0-py3-none-any.whl\n"
    )
    assert verify_distribution._verify_artifact_hashes(tmp_path) is True


def test_verify_artifact_hashes_mismatch(tmp_path: Path) -> None:
    """When a file hash does not match, verification fails."""
    (tmp_path / "file.whl").write_bytes(b"content")
    (tmp_path / "SHA256SUMS.txt").write_text("wrong_hash  file.whl\n")
    assert verify_distribution._verify_artifact_hashes(tmp_path) is False


def test_verify_artifact_hashes_missing_sums_file(tmp_path: Path) -> None:
    """When SHA256SUMS.txt is missing, verification fails."""
    (tmp_path / "file.whl").write_bytes(b"x")
    assert verify_distribution._verify_artifact_hashes(tmp_path) is False


def test_validate_sbom_valid(tmp_path: Path) -> None:
    """Valid CycloneDX-style JSON with components passes."""
    sbom = tmp_path / "sbom.json"
    sbom.write_text(json.dumps({"components": [{"name": "ezra", "version": "1.0.0"}]}))
    assert verify_distribution._validate_sbom(sbom) is True


def test_validate_sbom_valid_with_dependencies(tmp_path: Path) -> None:
    """SBOM with dependencies key but no components is accepted (structure check)."""
    sbom = tmp_path / "sbom.json"
    sbom.write_text(json.dumps({"dependencies": [{"ref": "pkg:py/ezra@1.0.0"}]}))
    assert verify_distribution._validate_sbom(sbom) is True


def test_validate_sbom_invalid_json(tmp_path: Path) -> None:
    """Invalid JSON fails."""
    sbom = tmp_path / "sbom.json"
    sbom.write_text("not json")
    assert verify_distribution._validate_sbom(sbom) is False


def test_validate_sbom_empty_components(tmp_path: Path) -> None:
    """Empty components and no dependencies fails."""
    sbom = tmp_path / "sbom.json"
    sbom.write_text(json.dumps({"components": []}))
    assert verify_distribution._validate_sbom(sbom) is False


def test_validate_provenance_valid(tmp_path: Path) -> None:
    """Provenance with required keys passes."""
    prov = tmp_path / "provenance.json"
    prov.write_text(
        json.dumps(
            {
                "commit": "abc123",
                "builder": "github-actions",
                "workflow": "Release",
                "artifact_hashes": {"ezra-1.0.0.whl": "deadbeef"},
            }
        )
    )
    assert verify_distribution._validate_provenance(prov) is True


def test_validate_provenance_missing_key(tmp_path: Path) -> None:
    """Provenance missing a required key fails."""
    prov = tmp_path / "provenance.json"
    prov.write_text(json.dumps({"commit": "abc", "builder": "x"}))
    assert verify_distribution._validate_provenance(prov) is False


def test_validate_provenance_invalid_json(tmp_path: Path) -> None:
    """Invalid JSON fails."""
    prov = tmp_path / "provenance.json"
    prov.write_text("{ invalid }")
    assert verify_distribution._validate_provenance(prov) is False


def test_script_exits_2_without_repo(monkeypatch: pytest.MonkeyPatch) -> None:
    """Script returns 2 when GITHUB_REPOSITORY is missing."""
    monkeypatch.setenv("GITHUB_REPOSITORY", "")
    monkeypatch.setenv("GITHUB_TOKEN", "dummy")
    monkeypatch.setattr(sys, "argv", ["verify_distribution.py", "--tag", "v1.0.0"])
    assert verify_distribution.main() == 2


def test_script_exits_2_without_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Script returns 2 when GITHUB_TOKEN is missing."""
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setenv("GITHUB_TOKEN", "")
    monkeypatch.setattr(sys, "argv", ["verify_distribution.py", "--tag", "v1.0.0"])
    assert verify_distribution.main() == 2
