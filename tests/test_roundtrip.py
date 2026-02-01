"""Test roundtrip encoding/decoding for all strategy combinations."""

import pytest
from pathlib import Path

from src.blob import BlobEncoder
from src.compression import COMPRESSORS
from src.packing import PACKERS
from src.tx_list_encoding import ENCODERS, get_encoder
from src.payload import load_transactions


# Get a sample payload for testing
PAYLOADS_DIR = Path("payloads")


def get_sample_payload() -> Path:
    """Get first available payload file."""
    files = list(PAYLOADS_DIR.glob("*.json"))
    if not files:
        pytest.skip("No payload files available")
    return files[0]


@pytest.fixture
def sample_transactions() -> list[bytes]:
    """Load transactions from a sample payload."""
    payload_file = get_sample_payload()
    return load_transactions(payload_file)


@pytest.mark.parametrize("encoder_name", list(ENCODERS.keys()))
def test_tx_list_encoder_roundtrip(encoder_name: str, sample_transactions: list[bytes]):
    """Test transaction list encoder roundtrip."""
    encoder = get_encoder(encoder_name)

    encoded = encoder.encode(sample_transactions)
    decoded = encoder.decode(encoded)

    assert decoded == sample_transactions, f"{encoder_name} roundtrip failed"


@pytest.mark.parametrize("compression", list(COMPRESSORS.keys()))
@pytest.mark.parametrize("packing", list(PACKERS.keys()))
def test_blob_encoder_roundtrip(compression: str, packing: str, sample_transactions: list[bytes]):
    """Test blob encoder roundtrip for all compression/packing combinations."""
    # First encode transactions to bytes
    tx_encoder = get_encoder("rlp")
    data = tx_encoder.encode(sample_transactions)

    # Then test blob encoding roundtrip
    blob_encoder = BlobEncoder.from_names(compression, packing)
    blobs, _ = blob_encoder.encode(data)
    decoded = blob_encoder.decode(blobs)

    assert decoded == data, f"{compression}+{packing} roundtrip failed"


@pytest.mark.parametrize("encoder_name", list(ENCODERS.keys()))
@pytest.mark.parametrize("compression", list(COMPRESSORS.keys()))
@pytest.mark.parametrize("packing", list(PACKERS.keys()))
def test_full_roundtrip(encoder_name: str, compression: str, packing: str, sample_transactions: list[bytes]):
    """Test full roundtrip: transactions -> encoded -> blobs -> decoded -> transactions."""
    # Encode transactions
    tx_encoder = get_encoder(encoder_name)
    data = tx_encoder.encode(sample_transactions)

    # Encode to blobs
    blob_encoder = BlobEncoder.from_names(compression, packing)
    blobs, _ = blob_encoder.encode(data)

    # Decode from blobs
    decoded_data = blob_encoder.decode(blobs)

    # Decode transactions
    decoded_txs = tx_encoder.decode(decoded_data)

    assert decoded_txs == sample_transactions, f"{encoder_name}+{compression}+{packing} full roundtrip failed"
