#!/usr/bin/env python3
"""EPB bundle determinism checker for CI gate.

This script verifies that EPB bundle emission produces byte-identical
outputs across multiple runs with identical inputs.

Usage:
    python scripts/check_determinism.py [--output-dir DIR] [--runs N]

Exit codes:
    0: All runs produced identical bundles
    1: Bundles differ between runs
    2: Error during execution
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

# Fixed timestamp for determinism testing
FIXED_TIMESTAMP = datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)


def compute_directory_hash(directory: Path) -> str:
    """Compute canonical SHA256 hash of directory contents.

    Walks directory recursively, sorts paths lexicographically,
    hashes each file's bytes, and combines into a single hash.

    Args:
        directory: Directory path to hash.

    Returns:
        Lowercase hexadecimal SHA256 hash (64 characters).
    """
    file_hashes: list[str] = []

    # Walk directory and collect all files
    for file_path in sorted(directory.rglob("*")):
        if file_path.is_file():
            # Compute hash of file contents
            file_bytes = file_path.read_bytes()
            file_hash = hashlib.sha256(file_bytes).hexdigest()

            # Use relative path for canonical ordering
            rel_path = file_path.relative_to(directory)
            file_hashes.append(f"{rel_path}:{file_hash}")

    # Combine all file hashes into single string
    combined = "\n".join(file_hashes)

    # Compute final hash
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


def generate_epb_bundle(output_dir: Path, run_number: int) -> Path:
    """Generate an EPB bundle with fixed inputs.

    Args:
        output_dir: Base output directory.
        run_number: Run number (1, 2, 3, ...).

    Returns:
        Path to generated bundle directory.
    """
    from ezra.epb import build_epb_bundle, write_epb_bundle

    # Fixed input fixture (identical across all runs)
    detections = [
        {"text": "Hello", "confidence": 0.9, "bbox": [10.0, 20.0, 50.0, 40.0]},
        {"text": "World", "confidence": 0.85, "bbox": [60.0, 20.0, 100.0, 40.0]},
    ]
    input_metadata = {"width": 200, "height": 100, "channels": 3}

    # Build bundle with fixed timestamp
    bundle = build_epb_bundle(
        detections=detections,
        plugin_name="test",
        plugin_version="1.0.0",
        input_metadata=input_metadata,
        timestamp=FIXED_TIMESTAMP,
    )

    # Write bundle to directory
    bundle_dir = output_dir / f"bundle_run_{run_number}"
    write_epb_bundle(bundle, bundle_dir)

    return bundle_dir


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check EPB bundle determinism")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("determinism_output"),
        help="Output directory for bundles (default: determinism_output)",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=3,
        help="Number of runs to compare (default: 3)",
    )
    args = parser.parse_args()

    output_dir = args.output_dir
    num_runs = args.runs

    if num_runs < 2:
        print("Error: --runs must be at least 2", file=sys.stderr)
        return 2

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate bundles
    bundle_dirs: list[Path] = []
    bundle_hashes: list[str] = []

    print(f"Generating {num_runs} EPB bundles with fixed inputs...")
    for run_num in range(1, num_runs + 1):
        bundle_dir = generate_epb_bundle(output_dir, run_num)
        bundle_hash = compute_directory_hash(bundle_dir)
        bundle_dirs.append(bundle_dir)
        bundle_hashes.append(bundle_hash)
        print(f"  Run {run_num}: {bundle_dir.name} -> SHA256: {bundle_hash}")

    # Compare hashes
    first_hash = bundle_hashes[0]
    all_identical = all(hash_val == first_hash for hash_val in bundle_hashes)

    # Build report
    report = {
        "determinism_check": {
            "num_runs": num_runs,
            "result": "PASS" if all_identical else "FAIL",
            "hashes": {
                f"run_{i+1}": {
                    "bundle_dir": str(bundle_dirs[i].name),
                    "sha256": bundle_hashes[i],
                }
                for i in range(num_runs)
            },
            "all_identical": all_identical,
        }
    }

    # Write report
    report_path = output_dir / "determinism_report.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nReport written to: {report_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("Determinism Gate Summary")
    print("=" * 60)
    for i, hash_val in enumerate(bundle_hashes, 1):
        print(f"SHA{i}: {hash_val}")
    print(f"Result: {report['determinism_check']['result']}")
    print("=" * 60)

    if not all_identical:
        print("\nFAIL: Bundles differ between runs", file=sys.stderr)
        print("This indicates nondeterminism in EPB bundle emission.", file=sys.stderr)
        return 1

    print("\nPASS: All bundles are byte-identical")
    return 0


if __name__ == "__main__":
    sys.exit(main())

