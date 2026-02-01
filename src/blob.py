"""Blob encoding combining compression and packing strategies."""

from .compression import Compressor, get_compressor
from .packing import Packer, get_packer


class BlobEncoder:
    """Encode data into blobs using a compression + packing strategy."""

    def __init__(self, compressor: Compressor, packer: Packer):
        self.compressor = compressor
        self.packer = packer

    @classmethod
    def from_names(cls, compression: str, packing: str) -> "BlobEncoder":
        """Create encoder from strategy names."""
        return cls(get_compressor(compression), get_packer(packing))

    @property
    def name(self) -> str:
        """Strategy name for reporting."""
        return f"{self.compressor.name}+{self.packer.name}"

    def encode(self, data: bytes) -> tuple[list[bytes], int]:
        """Encode data into blobs.

        Returns:
            (blobs, compressed_size) - list of blobs and size after compression
        """
        # Compress
        compressed = self.compressor.compress(data)

        # Prepend compressed length for decoding
        # Use 4 bytes for length (supports up to ~4 GB)
        compressed_len_prefix = len(compressed).to_bytes(4, "big")
        payload = compressed_len_prefix + compressed

        # Pack into blobs
        blobs = self.packer.pack(payload)

        return blobs, len(compressed)

    def decode(self, blobs: list[bytes]) -> bytes:
        """Decode blobs back to original data."""
        # Unpack from blobs
        payload = self.packer.unpack(blobs)

        # Extract compressed length
        compressed_len = int.from_bytes(payload[:4], "big")

        # Extract compressed data
        compressed = payload[4 : 4 + compressed_len]

        # Decompress
        data = self.compressor.decompress(compressed)

        return data
