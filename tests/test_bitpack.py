"""Tests for bit-packing strategy."""

from src.packing.base import BYTES_PER_FIELD_ELEMENT, FIELD_ELEMENTS_PER_BLOB
from src.packing.bitpack import BitPacker


def test_bitpack_roundtrip_and_padding():
    packer = BitPacker()
    data = bytes(range(1, 201))  # 200 bytes which is not aligned to 254-bit chunks

    blobs = packer.pack(data)
    assert blobs

    unpacked = packer.unpack(blobs)
    assert unpacked[: len(data)] == data
    assert set(unpacked[len(data) :]) <= {0}
    assert len(unpacked) == len(blobs) * packer.usable_bytes_per_blob


def test_bitpack_pack_empty_returns_no_blobs():
    packer = BitPacker()
    blobs = packer.pack(b"")

    assert blobs == []
    assert packer.unpack(blobs) == b""


def test_bitpack_elements_under_2_254():
    packer = BitPacker()
    data = bytes(range(1, 100))

    blobs = packer.pack(data)
    assert blobs

    limit = 1 << packer.bits_per_element
    for blob in blobs:
        for i in range(FIELD_ELEMENTS_PER_BLOB):
            offset = i * BYTES_PER_FIELD_ELEMENT
            elem = blob[offset : offset + BYTES_PER_FIELD_ELEMENT]
            assert int.from_bytes(elem, "big") < limit
