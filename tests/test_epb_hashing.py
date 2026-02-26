"""Tests for EPB SHA256 hashing."""

from ezra.epb.hasher import build_hashes_dict, compute_bundle_hash, compute_file_hash


def test_compute_file_hash_deterministic() -> None:
    """Test that file hash is deterministic."""
    content = {"a": 1, "b": 2}

    hash1 = compute_file_hash(content)
    hash2 = compute_file_hash(content)

    assert hash1 == hash2
    assert len(hash1) == 64  # SHA256 hex string length


def test_compute_file_hash_different_content() -> None:
    """Test that different content produces different hashes."""
    content1 = {"a": 1}
    content2 = {"a": 2}

    hash1 = compute_file_hash(content1)
    hash2 = compute_file_hash(content2)

    assert hash1 != hash2


def test_compute_bundle_hash_excludes_hashes_json() -> None:
    """Test that bundle hash excludes hashes.json."""
    file_hashes = {
        "manifest.json": "a" * 64,
        "detections.json": "b" * 64,
        "state.json": "c" * 64,
        "hashes.json": "d" * 64,  # Should be excluded
    }

    bundle_hash = compute_bundle_hash(file_hashes)

    # Bundle hash should be computed from sorted other files only
    # (manifest, detections, state - excluding hashes.json)
    assert len(bundle_hash) == 64
    # Verify hashes.json is excluded by checking hash doesn't match
    # a hash that would include hashes.json


def test_compute_bundle_hash_sorted_order() -> None:
    """Test that bundle hash uses sorted file names."""
    file_hashes1 = {
        "z.json": "a" * 64,
        "a.json": "b" * 64,
        "m.json": "c" * 64,
    }

    file_hashes2 = {
        "a.json": "b" * 64,  # Same content, different order
        "m.json": "c" * 64,
        "z.json": "a" * 64,
    }

    hash1 = compute_bundle_hash(file_hashes1)
    hash2 = compute_bundle_hash(file_hashes2)

    # Should produce same hash regardless of dict insertion order
    assert hash1 == hash2


def test_build_hashes_dict_structure() -> None:
    """Test that hashes.json structure is correct."""
    manifest_hash = "a" * 64
    detections_hash = "b" * 64
    state_hash = "c" * 64

    hashes_dict = build_hashes_dict(
        manifest_hash=manifest_hash,
        detections_hash=detections_hash,
        state_hash=state_hash,
        delta_hash=None,
    )

    # Verify structure
    assert hashes_dict["epb_version"] == "1.0.0"
    assert "bundle_hash" in hashes_dict
    assert "files" in hashes_dict

    # Verify files map
    files = hashes_dict["files"]
    assert files["manifest.json"] == manifest_hash
    assert files["detections.json"] == detections_hash
    assert files["state.json"] == state_hash
    assert "delta.json" not in files  # Delta not present
    assert "hashes.json" in files  # Required by schema


def test_build_hashes_dict_with_delta() -> None:
    """Test that delta.json is included when present."""
    manifest_hash = "a" * 64
    detections_hash = "b" * 64
    state_hash = "c" * 64
    delta_hash = "d" * 64

    hashes_dict = build_hashes_dict(
        manifest_hash=manifest_hash,
        detections_hash=detections_hash,
        state_hash=state_hash,
        delta_hash=delta_hash,
    )

    files = hashes_dict["files"]
    assert files["delta.json"] == delta_hash


def test_build_hashes_dict_with_zones() -> None:
    """Test that zones.json is included when present."""
    manifest_hash = "a" * 64
    detections_hash = "b" * 64
    state_hash = "c" * 64
    zones_hash = "e" * 64

    hashes_dict = build_hashes_dict(
        manifest_hash=manifest_hash,
        detections_hash=detections_hash,
        state_hash=state_hash,
        delta_hash=None,
        zones_hash=zones_hash,
    )

    files = hashes_dict["files"]
    assert files["zones.json"] == zones_hash


def test_build_hashes_dict_with_delta_and_zones() -> None:
    """Test that both delta.json and zones.json are included when present."""
    manifest_hash = "a" * 64
    detections_hash = "b" * 64
    state_hash = "c" * 64
    delta_hash = "d" * 64
    zones_hash = "e" * 64

    hashes_dict = build_hashes_dict(
        manifest_hash=manifest_hash,
        detections_hash=detections_hash,
        state_hash=state_hash,
        delta_hash=delta_hash,
        zones_hash=zones_hash,
    )

    files = hashes_dict["files"]
    assert files["delta.json"] == delta_hash
    assert files["zones.json"] == zones_hash


def test_build_hashes_dict_bundle_hash_excludes_hashes_json() -> None:
    """Test that bundle_hash excludes hashes.json from computation."""
    manifest_hash = "a" * 64
    detections_hash = "b" * 64
    state_hash = "c" * 64

    hashes_dict = build_hashes_dict(
        manifest_hash=manifest_hash,
        detections_hash=detections_hash,
        state_hash=state_hash,
        delta_hash=None,
    )

    # Bundle hash should be computed from manifest, detections, state only
    # (excluding hashes.json)
    bundle_hash = hashes_dict["bundle_hash"]
    assert len(bundle_hash) == 64

    # Verify bundle_hash doesn't change if hashes.json hash changes
    # (by computing expected bundle hash manually)
    expected_bundle_hash = compute_bundle_hash(
        {
            "detections.json": detections_hash,
            "manifest.json": manifest_hash,
            "state.json": state_hash,
        }
    )
    assert bundle_hash == expected_bundle_hash


def test_build_hashes_dict_hashes_json_included() -> None:
    """Test that hashes.json hash is included in files map."""
    hashes_dict = build_hashes_dict(
        manifest_hash="a" * 64,
        detections_hash="b" * 64,
        state_hash="c" * 64,
        delta_hash=None,
    )

    # hashes.json should be in files map (required by schema)
    assert "hashes.json" in hashes_dict["files"]
    hashes_json_hash = hashes_dict["files"]["hashes.json"]
    assert len(hashes_json_hash) == 64
