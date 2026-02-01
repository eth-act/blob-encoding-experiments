# Blob Encoding Experiments

Benchmark different strategies for encoding the list of transactions into blobs.

## What This Does

Takes Ethereum block transactions and tests different encoding pipelines:

```text
Transactions → Encode (RLP/SSZ) → Compress (none/zstd/gzip) → Pack into Blobs (31-byte/254-bit)
```

Note: Encode (RLP/SSZ) is for the transaction list. The transactions themselves are already RLP encoded. In the future, we could experiment SSZing the transactions too (See EIP-7807)

We measure: 

- blob count
- compression ratio
- encode/decode

For each strategy combination

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### 1. Fetch Blocks

Fetches beacon blocks using the Beacon API and extracts the execution payload:

```bash
# Fetch last 100 beacon blocks (default)
python fetch_blocks.py

# Fetch specific count
python fetch_blocks.py -c 50

# Fetch from specific slot
python fetch_blocks.py -s 9000000 -c 100

# Use different beacon node
python fetch_blocks.py -b https://your-beacon-node.com
```

Blocks are saved to `payloads/` as JSON files.

### 2. Run Benchmarks

```bash
python main.py
```

This tests all strategy combinations:

- **Tx List Encoding**: RLP, SSZ
- **Compression**: none, zstd (level 22), gzip (level 9)
- **Packing**: naive_31 (31 bytes/element), bitpack_254 (254 bits/element)

Results are saved to `results/benchmark_YYYYMMDD_HHMMSS.json`.

### 3. View Results

Open <http://localhost:8000> in your browser. Copy a benchmark JSON to `site/results.json` to view it:

```bash
cp results/benchmark_*.json site/results.json
```

## How Block Fetching Works

We use the Beacon API to fetch blocks because it returns execution payloads with transactions already as raw bytes as we would expect if they were sent from the CL to the EL via engine API.

```text
GET /eth/v2/beacon/blocks/{slot}
```

The response contains:

```json
{
  "data": {
    "message": {
      "body": {
        "execution_payload": {
          "transactions": ["0x02f87...", "0x02f87..."],
          ...
        }
      }
    }
  }
}
```

We only care about the execution_payload as that is what gets put into blobs. Currently it is only the transactions, see EIP 8142 for more details.

## Strategies Explained

### Transaction List Encoding

Takes `list[bytes]` (raw transactions) and encodes to a single `bytes` blob.

- **RLP**: `rlp.encode([tx1, tx2, ...])` - Standard Ethereum encoding (baseline)
- **SSZ**: Simple Serialize with length-prefixed transactions - Used in consensus layer

Note: I imagine that this won't have that much of an impact since it's just encoding a List of byte lists.

### Compression

Takes encoded bytes and compresses them.

- **none**: Pass-through, no compression (baseline)
- **zstd**: Zstandard at level 22 (max compressoon)
- **gzip**: Gzip at level 9 (max compression)

### Blob Packing

Takes compressed bytes and packs into 128KB blobs. Each blob has 4096 field elements of 32 bytes, but the BLS12-381 scalar field modulus (~2^255) limits usable bits per element.

- **naive_31**: Use 31 bytes per element (127,008 bytes/blob) - Simple, zeroes the high byte
- **bitpack_254**: Use 254 bits per element (130,048 bytes/blob) - Bit-level packing

> TODO: There is an even tighter packing where we pack according to the modulus, however it is more complex.

## Adding New Strategies

### Adding a Compressor

Create `src/compression/mycompressor.py`:

```python
class MyCompressor:
    name = "mycomp"

    def compress(self, data: bytes) -> bytes:
        return my_compress(data)

    def decompress(self, data: bytes) -> bytes:
        return my_decompress(data)
```

Register in `src/compression/__init__.py`:

```python
from .mycompressor import MyCompressor

COMPRESSORS = {
    ...
    "mycomp": MyCompressor(),
}
```

### Adding a Packer

Create `src/packing/mypacker.py`:

```python
from .base import BLOB_SIZE, FIELD_ELEMENTS_PER_BLOB

class MyPacker:
    name = "mypacker"
    usable_bytes_per_blob = 127000  # How many data bytes fit in one blob

    def pack(self, data: bytes) -> list[bytes]:
        """Pack data into list of 128KB blobs."""
        blobs = []
        # ... pack data into blobs ...
        # Each blob must be exactly BLOB_SIZE (131072) bytes
        return blobs

    def unpack(self, blobs: list[bytes]) -> bytes:
        """Unpack blobs back to data."""
        # ... extract data from blobs ...
        return data
```

Register in `src/packing/__init__.py`:

```python
from .mypacker import MyPacker

PACKERS = {
    ...
    "mypacker": MyPacker(),
}
```

### Adding a Transaction List Encoder

Create `src/tx_list_encoding/myencoder.py`:

```python
class MyEncoder:
    name = "myenc"

    def encode(self, transactions: list[bytes]) -> bytes:
        """Encode list of raw transactions to bytes."""
        return encoded_data

    def decode(self, data: bytes) -> list[bytes]:
        """Decode bytes back to list of raw transactions."""
        return transactions
```

Register in `src/tx_list_encoding/__init__.py`:

```python
from .myencoder import MyEncoder

ENCODERS = {
    ...
    "myenc": MyEncoder(),
}
```

## Running Tests

```bash
pytest tests/ -v
```