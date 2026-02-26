"""Tests for EPB bundle builder."""

from ezra.epb.builder import EPB_VERSION, build_epb_bundle


def test_build_epb_bundle_minimal() -> None:
    """Test building minimal EPB bundle."""
    detections = [{"text": "Hello", "confidence": 0.9, "bbox": [10.0, 20.0, 50.0, 40.0]}]
    input_metadata = {"width": 100, "height": 200, "channels": 3}

    bundle = build_epb_bundle(
        detections=detections,
        plugin_name="easyocr",
        plugin_version="1.7.2",
        input_metadata=input_metadata,
    )

    # Verify structure
    assert "manifest" in bundle
    assert "detections" in bundle
    assert "state" in bundle
    assert bundle["delta"] is None

    # Verify manifest
    manifest = bundle["manifest"]
    assert manifest["epb_version"] == EPB_VERSION
    assert manifest["plugin_versions"]["easyocr"]["name"] == "easyocr"
    assert manifest["plugin_versions"]["easyocr"]["version"] == "1.7.2"
    assert manifest["input_metadata"] == input_metadata

    # Verify detections
    assert bundle["detections"]["detections"] == detections

    # Verify state is always present (minimal if None provided)
    assert bundle["state"] is not None
    assert "version" in bundle["state"]
    assert "timestamp" in bundle["state"]


def test_build_epb_bundle_with_state() -> None:
    """Test building EPB bundle with structured state."""
    detections = []
    input_metadata = {"width": 100, "height": 200, "channels": 3}
    state = {"zones": [{"id": "zone1", "bbox": [0, 0, 100, 100]}]}

    bundle = build_epb_bundle(
        detections=detections,
        plugin_name="tesseract",
        plugin_version="5.0.0",
        input_metadata=input_metadata,
        state=state,
    )

    # Verify state is merged with version and timestamp
    assert bundle["state"]["version"] == "1.0.0"
    assert "timestamp" in bundle["state"]
    assert bundle["state"]["zones"] == state["zones"]


def test_build_epb_bundle_with_delta() -> None:
    """Test building EPB bundle with delta."""
    detections = []
    input_metadata = {"width": 100, "height": 200, "channels": 3}
    delta = {"changes": [{"type": "add", "entity": "piece1"}]}

    bundle = build_epb_bundle(
        detections=detections,
        plugin_name="easyocr",
        plugin_version="1.7.2",
        input_metadata=input_metadata,
        delta=delta,
    )

    assert bundle["delta"] == delta


def test_build_epb_bundle_epb_version_immutable() -> None:
    """Test that EPB version is locked to 1.0.0."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    assert bundle["manifest"]["epb_version"] == "1.0.0"


def test_build_epb_bundle_platform_info() -> None:
    """Test that platform and Python version are included."""
    bundle = build_epb_bundle(
        detections=[],
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata={"width": 100, "height": 200, "channels": 3},
    )

    manifest = bundle["manifest"]
    assert "platform" in manifest
    assert "python_version" in manifest
    assert "timestamp" in manifest
