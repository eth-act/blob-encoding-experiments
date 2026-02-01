"""Base protocol for compression strategies."""

from typing import Protocol


class Compressor(Protocol):
    """Protocol for compression strategies."""

    name: str

    def compress(self, data: bytes) -> bytes:
        """Compress data."""
        ...

    def decompress(self, data: bytes) -> bytes:
        """Decompress data."""
        ...
