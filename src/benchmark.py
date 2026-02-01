"""Benchmark blob encoding strategies."""

import json
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

from .blob import BlobEncoder
from .compression import COMPRESSORS
from .tx_list_encoding import ENCODERS
from .packing import PACKERS
from .payload import load_transactions, get_encoder


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run."""

    encoding: str           # Transaction list encoding (rlp, ssz)
    compression: str        # Compression (none, zstd, gzip)
    packing: str            # Blob packing (naive, bitpack)
    payload_file: str
    raw_size: int           # Encoded transaction list size in bytes
    compressed_size: int    # After compression
    blob_count: int         # Number of blobs produced
    space_efficiency: float # raw_size / (blob_count * usable_blob_capacity)
    encode_time_ms: float   # Time to compress + pack
    decode_time_ms: float   # Time to unpack + decompress


def benchmark_single(
    data: bytes,
    blob_encoder: BlobEncoder,
    encoding_name: str,
    payload_file: str,
    iterations: int = 10,
) -> BenchmarkResult:
    """Run benchmark for a single encoder on a single payload."""
    raw_size = len(data)

    # Benchmark encoding
    encode_times = []
    blobs = None
    compressed_size = 0
    for _ in range(iterations):
        start = time.perf_counter()
        blobs, compressed_size = blob_encoder.encode(data)
        end = time.perf_counter()
        encode_times.append((end - start) * 1000)

    # Benchmark decoding
    decode_times = []
    for _ in range(iterations):
        start = time.perf_counter()
        blob_encoder.decode(blobs)
        end = time.perf_counter()
        decode_times.append((end - start) * 1000)

    # Calculate metrics
    blob_count = len(blobs)
    usable_per_blob = blob_encoder.packer.usable_bytes_per_blob
    space_efficiency = raw_size / (blob_count * usable_per_blob) if blob_count > 0 else 0

    return BenchmarkResult(
        encoding=encoding_name,
        compression=blob_encoder.compressor.name,
        packing=blob_encoder.packer.name,
        payload_file=payload_file,
        raw_size=raw_size,
        compressed_size=compressed_size,
        blob_count=blob_count,
        space_efficiency=space_efficiency,
        encode_time_ms=sum(encode_times) / len(encode_times),
        decode_time_ms=sum(decode_times) / len(decode_times),
    )


def run_benchmark(
    payload_files: list[Path],
    encoders: list[str] | None = None,
    compressors: list[str] | None = None,
    packers: list[str] | None = None,
    iterations: int = 10,
) -> list[BenchmarkResult]:
    """Run benchmark across all combinations."""
    if encoders is None:
        encoders = list(ENCODERS.keys())
    if compressors is None:
        compressors = list(COMPRESSORS.keys())
    if packers is None:
        packers = list(PACKERS.keys())

    results = []

    for payload_file in payload_files:
        print(f"Processing {payload_file.name}...")
        transactions = load_transactions(payload_file)

        for enc_name in encoders:
            tx_encoder = get_encoder(enc_name)
            data = tx_encoder.encode(transactions)

            for comp_name in compressors:
                for pack_name in packers:
                    blob_encoder = BlobEncoder.from_names(comp_name, pack_name)
                    result = benchmark_single(
                        data, blob_encoder, enc_name, payload_file.name, iterations
                    )
                    results.append(result)
                    print(f"  {enc_name}+{blob_encoder.name}: {result.blob_count} blobs, "
                          f"{result.space_efficiency:.2%} efficiency")

    return results


def save_results(results: list[BenchmarkResult], output_dir: Path) -> Path:
    """Save benchmark results to JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"benchmark_{timestamp}.json"

    with open(output_file, "w") as f:
        json.dump([asdict(r) for r in results], f, indent=2)

    return output_file
