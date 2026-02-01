"""Packing strategies for blob encoding."""

from .base import (
    Packer,
    FIELD_ELEMENTS_PER_BLOB,
    BYTES_PER_FIELD_ELEMENT,
    BLOB_SIZE,
    BLS_MODULUS,
)
from .naive import NaivePacker
from .bitpack import BitPacker

# Registry of available packers
PACKERS: dict[str, type[Packer]] = {
    "naive": NaivePacker,
    "bitpack": BitPacker,
}


def get_packer(name: str) -> Packer:
    """Get a packer by name."""
    if name not in PACKERS:
        raise ValueError(f"Unknown packer: {name}. Available: {list(PACKERS.keys())}")
    return PACKERS[name]()


__all__ = [
    "Packer",
    "FIELD_ELEMENTS_PER_BLOB",
    "BYTES_PER_FIELD_ELEMENT",
    "BLOB_SIZE",
    "BLS_MODULUS",
    "NaivePacker",
    "BitPacker",
    "PACKERS",
    "get_packer",
]
