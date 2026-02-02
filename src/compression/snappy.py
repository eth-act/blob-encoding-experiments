"""Snappy compression."""

import snappy


class SnappyCompressor:
    """Snappy compression - optimized for speed over ratio."""

    name = "snappy"

    def compress(self, data: bytes) -> bytes:
        return snappy.compress(data)

    def decompress(self, data: bytes) -> bytes:
        return snappy.decompress(data)
