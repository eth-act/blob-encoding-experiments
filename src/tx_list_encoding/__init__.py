"""Transaction list encoding strategies."""

from .base import TransactionListEncoder
from .rlp_encoder import RlpEncoder
from .ssz_encoder import SszEncoder

# Registry of available encoders
ENCODERS: dict[str, type[TransactionListEncoder]] = {
    "rlp": RlpEncoder,
    "ssz": SszEncoder,
}


def get_encoder(name: str) -> TransactionListEncoder:
    """Get an encoder by name."""
    if name not in ENCODERS:
        raise ValueError(f"Unknown encoder: {name}. Available: {list(ENCODERS.keys())}")
    return ENCODERS[name]()


__all__ = [
    "TransactionListEncoder",
    "RlpEncoder",
    "SszEncoder",
    "ENCODERS",
    "get_encoder",
]
