"""Tests for baseline canonicalization utilities."""

from ezra.baseline.canonicalize import (
    canonicalize_detections,
    canonicalize_output,
    to_canonical_json,
)


def test_canonicalize_detections_sorting() -> None:
    """Test that detections are sorted by top-left corner (y, then x)."""
    detections = [
        {"text": "B", "confidence": 0.9, "bbox": [50.0, 20.0, 80.0, 40.0]},  # y=20
        {"text": "A", "confidence": 0.8, "bbox": [10.0, 10.0, 40.0, 30.0]},  # y=10
        {"text": "C", "confidence": 0.95, "bbox": [10.0, 20.0, 40.0, 40.0]},  # y=20, x=10
    ]

    canonicalized = canonicalize_detections(detections)

    # Should be sorted: A (y=10), then B (y=20, x=50), then C (y=20, x=10)
    assert canonicalized[0]["text"] == "A"
    assert canonicalized[1]["text"] == "C"  # Same y, but x=10 < x=50
    assert canonicalized[2]["text"] == "B"


def test_canonicalize_detections_rounding() -> None:
    """Test that floats are rounded to 6 decimal places."""
    detections = [
        {
            "text": "Test",
            "confidence": 0.123456789,
            "bbox": [10.123456789, 20.987654321, 30.111111111, 40.999999999],
        }
    ]

    canonicalized = canonicalize_detections(detections)

    assert canonicalized[0]["confidence"] == 0.123457  # Rounded to 6 places
    assert canonicalized[0]["bbox"] == [
        10.123457,  # Rounded
        20.987654,  # Rounded
        30.111111,  # Rounded
        41.0,  # 40.999999 rounds to 41.0 at 6 decimal places
    ]


def test_canonicalize_detections_deterministic() -> None:
    """Test that canonicalization is deterministic (same input = same output)."""
    detections = [
        {"text": "A", "confidence": 0.8, "bbox": [10.0, 10.0, 40.0, 30.0]},
        {"text": "B", "confidence": 0.9, "bbox": [50.0, 20.0, 80.0, 40.0]},
    ]

    result1 = canonicalize_detections(detections)
    result2 = canonicalize_detections(detections)

    assert result1 == result2


def test_canonicalize_output() -> None:
    """Test canonicalize_output function."""
    output = {
        "detections": [
            {"text": "B", "confidence": 0.9, "bbox": [50.0, 20.0, 80.0, 40.0]},
            {"text": "A", "confidence": 0.8, "bbox": [10.0, 10.0, 40.0, 30.0]},
        ]
    }

    canonicalized = canonicalize_output(output)

    assert "detections" in canonicalized
    assert len(canonicalized["detections"]) == 2
    # Should be sorted
    assert canonicalized["detections"][0]["text"] == "A"
    assert canonicalized["detections"][1]["text"] == "B"


def test_canonicalize_output_no_detections() -> None:
    """Test canonicalize_output with missing detections key."""
    output = {"other_key": "value"}

    canonicalized = canonicalize_output(output)

    assert canonicalized == output  # Should return unchanged


def test_to_canonical_json() -> None:
    """Test JSON serialization with sorted keys."""
    obj = {"z": 3, "a": 1, "m": 2}

    json_str = to_canonical_json(obj)

    # Should be sorted by keys
    assert json_str.startswith("{\n  \"a\":")
    assert '"a"' in json_str
    assert '"m"' in json_str
    assert '"z"' in json_str


def test_to_canonical_json_deterministic() -> None:
    """Test that JSON serialization is deterministic."""
    obj = {"z": 3, "a": 1, "m": 2}

    json1 = to_canonical_json(obj)
    json2 = to_canonical_json(obj)

    assert json1 == json2

