"""Per-transaction compression with RLP encoding."""

import rlp

from ..compression import Compressor, get_compressor


class PerTxRlpEncoder:
    """Compress each transaction individually, then RLP encode the list.

    Encodes as: RLP([compress(tx1), compress(tx2), ...])
    This allows comparing per-tx vs bulk compression efficiency.
    """

    def __init__(self, compressor: Compressor):
        self.compressor = compressor

    @property
    def name(self) -> str:
        return f"rlp_pertx_{self.compressor.name}"

    def encode(self, transactions: list[bytes]) -> bytes:
        compressed_txs = [self.compressor.compress(tx) for tx in transactions]
        return rlp.encode(compressed_txs)

    def decode(self, data: bytes) -> list[bytes]:
        compressed_txs = rlp.decode(data)
        return [self.compressor.decompress(tx) for tx in compressed_txs]


def make_pertx_encoder(compression: str) -> PerTxRlpEncoder:
    """Factory to create per-tx encoder with specified compression."""
    return PerTxRlpEncoder(get_compressor(compression))
