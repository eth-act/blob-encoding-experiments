"""Compression strategies for blob encoding."""

from .base import Compressor
from .none import NoCompression
from .zstd import ZstdCompressor
from .gzip import GzipCompressor


class ZstdFastCompressor(ZstdCompressor):
    """Zstandard at level 3 - fast compression."""

    name = "zstd_fast"

    def __init__(self):
        super().__init__(level=3)


class ZstdMidCompressor(ZstdCompressor):
    """Zstandard at level 6 - balanced compression."""

    name = "zstd_mid"

    def __init__(self):
        super().__init__(level=6)


# Registry of available compressors
COMPRESSORS: dict[str, type[Compressor]] = {
    "none": NoCompression,
    "zstd": ZstdCompressor,
    "zstd_fast": ZstdFastCompressor,
    "zstd_mid": ZstdMidCompressor,
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
