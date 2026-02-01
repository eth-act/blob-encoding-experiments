"""Base protocol and constants for packing strategies."""

from typing import Protocol

# Blob constants
FIELD_ELEMENTS_PER_BLOB = 4096
BYTES_PER_FIELD_ELEMENT = 32
BLOB_SIZE = FIELD_ELEMENTS_PER_BLOB * BYTES_PER_FIELD_ELEMENT  # 131072 bytes (~128KB)

# BLS12-381 scalar field modulus
BLS_MODULUS = 0x73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000001


class Packer(Protocol):
    """Protocol for packing strategies."""

    name: str
    usable_bytes_per_blob: int

    def pack(self, data: bytes) -> list[bytes]:
        """Pack data into blobs. Returns list of 128KB blobs."""
        ...

    def unpack(self, blobs: list[bytes]) -> bytes:
        """Unpack blobs back to original data."""
        ...
