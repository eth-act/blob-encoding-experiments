"""RLP encoding for transaction lists."""

import rlp


class RlpEncoder:
    """RLP encode transaction list.

    Encodes as: RLP([tx1, tx2, ...])
    Each tx is already RLP-encoded, so this wraps them in a list.
    """

    name = "rlp"

    def encode(self, transactions: list[bytes]) -> bytes:
        return rlp.encode(transactions)

    def decode(self, data: bytes) -> list[bytes]:
        return rlp.decode(data)
