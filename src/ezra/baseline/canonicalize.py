"""Canonicalization utilities for deterministic baseline outputs."""

from __future__ import annotations

import json
from typing import Any


def canonicalize_detections(detections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Canonicalize detection list for stable comparison.

    Sorts detections deterministically and rounds floats to fixed precision.

    Args:
        detections: List of detection dictionaries, each containing:
            - "text": str
            - "confidence": float
            - "bbox": list[float] [x1, y1, x2, y2]

    Returns:
        Canonicalized list of detections, sorted by top-left corner (y, then x),
        with floats rounded to 6 decimal places.
    """
    # Round floats to 6 decimal places for stability
    precision = 6

    canonicalized = []
    for det in detections:
        canonicalized.append(
            {
                "text": str(det["text"]),
                "confidence": round(float(det["confidence"]), precision),
                "bbox": [round(float(coord), precision) for coord in det["bbox"]],
            }
        )

    # Sort by top-left corner: first by y1, then by x1
    canonicalized.sort(key=lambda d: (d["bbox"][1], d["bbox"][0]))  # type: ignore[index]

    return canonicalized


def canonicalize_output(output: dict[str, Any]) -> dict[str, Any]:
    """Canonicalize full OCR output dictionary.

    Args:
        output: Dictionary containing "detections" key with list of detections.

    Returns:
        Canonicalized output with sorted, rounded detections.
    """
    if "detections" not in output:
        return output

    return {
        "detections": canonicalize_detections(output["detections"]),
    }


def to_canonical_json(obj: Any) -> str:
    """Convert object to canonical JSON string.

    Uses deterministic sorting and fixed float precision.

    Args:
        obj: Object to serialize (typically dict or list).

    Returns:
        Canonical JSON string with sorted keys and rounded floats.
    """
    return json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False)
