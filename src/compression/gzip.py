"""Gzip compression."""

import gzip as gzip_lib


class GzipCompressor:
    """Gzip compression."""

    name = "gzip"

    def __init__(self, level: int = 9):
        self.level = level

    def compress(self, data: bytes) -> bytes:
        return gzip_lib.compress(data, compresslevel=self.level)

    def decompress(self, data: bytes) -> bytes:
        return gzip_lib.decompress(data)
