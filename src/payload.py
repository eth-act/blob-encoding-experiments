"""Load ExecutionPayload JSON and extract transactions."""

import json
from pathlib import Path

from .tx_list_encoding import get_encoder


def load_payload(path: Path) -> dict:
    """Load an ExecutionPayload from a JSON file."""
    with open(path) as f:
        return json.load(f)


def extract_transactions(payload: dict) -> list[bytes]:
    """Extract transactions from an ExecutionPayload.

    Transactions in the payload are hex-encoded strings.
    Returns list of raw transaction bytes.
    """
    transactions = payload.get("transactions", [])
    result = []
    for tx in transactions:
        # Remove 0x prefix if present
        tx_hex = tx[2:] if tx.startswith("0x") else tx
        result.append(bytes.fromhex(tx_hex))
    return result


def load_transactions(path: Path) -> list[bytes]:
    """Load payload and return list of raw transaction bytes."""
    payload = load_payload(path)
    return extract_transactions(payload)


def load_and_encode(path: Path, encoder_name: str = "rlp") -> bytes:
    """Load payload and encode transactions.

    Args:
        path: Path to payload JSON file
        encoder_name: Encoder to use ("rlp" or "ssz")

    Returns:
        Encoded transaction bytes
    """
    transactions = load_transactions(path)
    encoder = get_encoder(encoder_name)
    return encoder.encode(transactions)
