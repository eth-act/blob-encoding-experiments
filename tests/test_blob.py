"""Tests for BlobEncoder payload layout."""

from src.blob import BlobEncoder
from src.compression.none import NoCompression


class _SpyPacker:
    name = "spy"
    usable_bytes_per_blob = 0

    def __init__(self):
        self.last_payload = b""

    def pack(self, data: bytes) -> list[bytes]:
        self.last_payload = data
        return [data]

    def unpack(self, blobs: list[bytes]) -> bytes:
        return blobs[0] if blobs else b""


def test_blob_encoder_stores_only_compressed_length_prefix():
    packer = _SpyPacker()
    encoder = BlobEncoder(NoCompression(), packer)
    data = b"hello world"

    encoder.encode(data)

    assert packer.last_payload[:4] == len(data).to_bytes(4, "big")
    assert len(packer.last_payload) == 4 + len(data)
