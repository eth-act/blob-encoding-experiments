"""Tests for naive packing strategy."""

from src.packing.naive import NaivePacker


def test_naive_pack_empty_returns_no_blobs():
    packer = NaivePacker()
    blobs = packer.pack(b"")

    assert blobs == []
    assert packer.unpack(blobs) == b""
