"""Base protocol for transaction list encoding."""

from typing import Protocol


class TransactionListEncoder(Protocol):
    """Protocol for encoding a list of transactions."""

    name: str

    def encode(self, transactions: list[bytes]) -> bytes:
        """Encode a list of transactions to bytes."""
        ...

    def decode(self, data: bytes) -> list[bytes]:
        """Decode bytes back to a list of transactions."""
        ...
