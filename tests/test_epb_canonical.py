"""Tests for EPB canonical JSON serialization."""

import json

import pytest

from ezra.epb.canonical import EPB_FLOAT_PRECISION, canonicalize_float, to_canonical_json


def test_canonicalize_float_rounding() -> None:
    """Test that floats are rounded to 8 decimal places."""
    value = 0.123456789012345
    result = canonicalize_float(value)
    assert result == 0.12345679  # Rounded to 8 decimal places


def test_canonicalize_float_rejects_nan() -> None:
    """Test that NaN values are rejected."""
    with pytest.raises(ValueError, match="NaN values are not permitted"):
        canonicalize_float(float("nan"))


def test_canonicalize_float_rejects_infinity() -> None:
    """Test that Infinity values are rejected."""
    with pytest.raises(ValueError, match="Infinity values are not permitted"):
        canonicalize_float(float("inf"))

    with pytest.raises(ValueError, match="Infinity values are not permitted"):
        canonicalize_float(float("-inf"))


def test_to_canonical_json_sorted_keys() -> None:
    """Test that JSON keys are sorted alphabetically."""
    obj = {"z": 3, "a": 1, "m": 2}
    json_str = to_canonical_json(obj)

    # Parse back to verify order
    parsed = json.loads(json_str)
    keys = list(parsed.keys())
    assert keys == ["a", "m", "z"]


def test_to_canonical_json_indented() -> None:
    """Test that JSON is indented with 2 spaces."""
    obj = {"a": 1, "b": {"c": 2}}
    json_str = to_canonical_json(obj)

    # Should contain newlines and 2-space indentation
    assert "\n" in json_str
    assert "  " in json_str  # 2 spaces


def test_to_canonical_json_float_precision() -> None:
    """Test that floats are rounded to 8 decimal places in JSON."""
    obj = {"value": 0.123456789012345}
    json_str = to_canonical_json(obj)

    # Parse back and verify precision
    parsed = json.loads(json_str)
    assert parsed["value"] == 0.12345679


def test_to_canonical_json_deterministic() -> None:
    """Test that JSON serialization is deterministic."""
    obj = {"z": 3, "a": 1, "m": 2, "float": 0.123456789}
    json1 = to_canonical_json(obj)
    json2 = to_canonical_json(obj)

    assert json1 == json2


def test_to_canonical_json_nested_dicts() -> None:
    """Test that nested dictionaries are sorted recursively."""
    obj = {
        "z": {"c": 3, "a": 1, "b": 2},
        "a": {"z": 3, "a": 1},
    }
    json_str = to_canonical_json(obj)

    # Parse back and verify nested keys are sorted
    parsed = json.loads(json_str)
    assert list(parsed["a"].keys()) == ["a", "z"]
    assert list(parsed["z"].keys()) == ["a", "b", "c"]


def test_to_canonical_json_arrays_preserve_order() -> None:
    """Test that arrays preserve order (arrays are ordered structures)."""
    obj = {"items": [3, 1, 2]}
    json_str = to_canonical_json(obj)

    # Parse back and verify order preserved
    parsed = json.loads(json_str)
    assert parsed["items"] == [3, 1, 2]


def test_to_canonical_json_rejects_nan() -> None:
    """Test that NaN values in objects are rejected."""
    obj = {"value": float("nan")}
    with pytest.raises(ValueError, match="NaN"):
        to_canonical_json(obj)


def test_to_canonical_json_rejects_infinity() -> None:
    """Test that Infinity values in objects are rejected."""
    obj = {"value": float("inf")}
    with pytest.raises(ValueError, match="Infinity"):
        to_canonical_json(obj)


def test_to_canonical_json_utf8() -> None:
    """Test that UTF-8 characters are preserved (ensure_ascii=False)."""
    obj = {"text": "Hello 世界"}
    json_str = to_canonical_json(obj)

    # Should contain Unicode characters directly (not escaped)
    assert "世界" in json_str
    assert "\\u" not in json_str or json_str.count("\\u") == 0


def test_epb_float_precision_constant() -> None:
    """Test that EPB_FLOAT_PRECISION constant is 8."""
    assert EPB_FLOAT_PRECISION == 8
