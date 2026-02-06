"""Transaction list encoding strategies."""

from .base import TransactionListEncoder
from .rlp_encoder import RlpEncoder
from .ssz_encoder import SszEncoder
from .pertx_rlp_encoder import PerTxRlpEncoder, make_pertx_encoder

# Registry of available encoders (classes that take no args)
ENCODERS: dict[str, type[TransactionListEncoder]] = {
    "rlp": RlpEncoder,
    "ssz": SszEncoder,
}

# Per-tx compression variants to test
PERTX_COMPRESSIONS = ["zstd_3", "snappy"]


def get_encoder(name: str) -> TransactionListEncoder:
    """Get an encoder by name."""
    # Check for per-tx variants (e.g., "rlp_pertx_zstd_3")
    if name.startswith("rlp_pertx_"):
        compression = name.replace("rlp_pertx_", "")
        return make_pertx_encoder(compression)

    if name not in ENCODERS:
        raise ValueError(f"Unknown encoder: {name}. Available: {list(ENCODERS.keys())}")
    return ENCODERS[name]()


__all__ = [
    "TransactionListEncoder",
    "RlpEncoder",
    "SszEncoder",
    "PerTxRlpEncoder",
    "ENCODERS",
    "PERTX_COMPRESSIONS",
    "get_encoder",
    "make_pertx_encoder",
]
