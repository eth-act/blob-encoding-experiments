"""Compression strategies for blob encoding."""

from .base import Compressor
from .none import NoCompression
from .zstd import ZstdCompressor
from .gzip import GzipCompressor

# Registry of available compressors
COMPRESSORS: dict[str, type[Compressor]] = {
    "none": NoCompression,
    "zstd": ZstdCompressor,
    "gzip": GzipCompressor,
}


def get_compressor(name: str) -> Compressor:
    """Get a compressor by name."""
    if name not in COMPRESSORS:
        raise ValueError(f"Unknown compressor: {name}. Available: {list(COMPRESSORS.keys())}")
    return COMPRESSORS[name]()


__all__ = [
    "Compressor",
    "NoCompression",
    "ZstdCompressor",
    "GzipCompressor",
    "COMPRESSORS",
    "get_compressor",
]
