"""SSZ encoding for transaction lists.

Uses the ssz library to encode transactions as List[ByteList].
"""

from ssz import decode, encode
from ssz.sedes import ByteList, List


# Max transaction size (2MB should be plenty)
MAX_TX_SIZE = 2**21
# Max transactions per block
MAX_TXS = 2**20

# SSZ sedes for List[ByteList]
TX_LIST_SEDES = List(ByteList(MAX_TX_SIZE), MAX_TXS)


class SszEncoder:
    """SSZ encode transaction list using the ssz library."""

    name = "ssz"

    def encode(self, transactions: list[bytes]) -> bytes:
        if not transactions:
            return b""
        return encode(transactions, TX_LIST_SEDES)

    def decode(self, data: bytes) -> list[bytes]:
        if not data:
            return []
        return list(decode(data, TX_LIST_SEDES))
