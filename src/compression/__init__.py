"""Compression strategies for blob encoding."""

from .base import Compressor
from .none import NoCompression
from .zstd import ZstdCompressor
from .gzip import GzipCompressor
from .snappy import SnappyCompressor


# Registry of available compressors (instantiated with specific levels)
COMPRESSORS: dict[str, Compressor] = {
    "none": NoCompression(),
    "snappy": SnappyCompressor(),
    "zstd_3": ZstdCompressor(level=3),
    "zstd_6": ZstdCompressor(level=6),
    "zstd_22": ZstdCompressor(level=22),
    "gzip_9": GzipCompressor(level=9),
}


def get_compressor(name: str) -> Compressor:
    """Get a compressor by name."""
    if name not in COMPRESSORS:
        raise ValueError(f"Unknown compressor: {name}. Available: {list(COMPRESSORS.keys())}")
    return COMPRESSORS[name]


__all__ = [
    "Compressor",
    "NoCompression",
    "ZstdCompressor",
    "GzipCompressor",
    "SnappyCompressor",
    "COMPRESSORS",
    "get_compressor",
]
