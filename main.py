#!/usr/bin/env python3
"""Run all blob encoding experiments."""

from collections import defaultdict
from pathlib import Path

from src.benchmark import run_benchmark, save_results
from src.compression import COMPRESSORS
from src.tx_list_encoding import ENCODERS
from src.packing import PACKERS


def main():
    payloads_dir = Path("payloads")
    results_dir = Path("results")
    iterations = 3

    # Find payload files
    payload_files = list(payloads_dir.glob("*.json"))
    if not payload_files:
        print(f"No JSON files found in {payloads_dir}")
        return

    # Show what we're testing
    num_combinations = len(ENCODERS) * len(COMPRESSORS) * len(PACKERS)
    print(f"Payloads: {len(payload_files)} files")
    print(f"Strategies: {num_combinations} combinations")
    print(f"  Encodings:    {list(ENCODERS.keys())}")
    print(f"  Compression:  {list(COMPRESSORS.keys())}")
    print(f"  Packing:      {list(PACKERS.keys())}")
    print()

    # Run benchmarks
    results = run_benchmark(payload_files, None, None, None, iterations)

    # Save results
    output_file = save_results(results, results_dir)
    print(f"\nResults saved to {output_file}")

    # Print aggregate summary
    print("\n" + "=" * 60)
    print("AGGREGATE RESULTS")
    print("=" * 60)

    # Group by strategy
    by_strategy: dict[str, dict[str, int]] = defaultdict(lambda: {"blobs": 0, "raw": 0})

    for r in results:
        key = f"{r.encoding}+{r.compression}+{r.packing}"
        by_strategy[key]["blobs"] += r.blob_count
        by_strategy[key]["raw"] += r.raw_size

    # Find baseline
    baseline_key = "rlp+none+naive_31"
    baseline_blobs = by_strategy[baseline_key]["blobs"]

    # Print sorted by blob count
    sorted_strategies = sorted(by_strategy.items(), key=lambda x: x[1]["blobs"])
    for key, stats in sorted_strategies:
        diff = stats["blobs"] - baseline_blobs
        pct = (diff / baseline_blobs) * 100 if baseline_blobs > 0 else 0
        print(f"{key:35} {stats['blobs']:4} blobs ({diff:+4}, {pct:+5.1f}%)")


if __name__ == "__main__":
    main()
