"""Zstandard compression."""

import zstandard as zstd


class ZstdCompressor:
    """Zstandard compression."""

    name = "zstd"

    def __init__(self, level: int = 22):
        self.level = level
        self._compressor = zstd.ZstdCompressor(level=level)
        self._decompressor = zstd.ZstdDecompressor()

    def compress(self, data: bytes) -> bytes:
        return self._compressor.compress(data)

    def decompress(self, data: bytes) -> bytes:
        return self._decompressor.decompress(data)
