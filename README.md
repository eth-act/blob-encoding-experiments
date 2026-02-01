# Blob Encoding Experiments

Benchmark different strategies for encoding the list of transactions into blobs.

## What This Does

Takes Ethereum block transactions and tests different encoding pipelines:

```text
Transactions → Tx List Encode (RLP/SSZ) → Compress (none/zstd/gzip) → Pack into Blobs (31-byte/254-bit)
```

Note: Tx List Encode (RLP/SSZ) is only the transaction list and not the transactions. The transactions themselves are already RLP encoded. In the future, we could experiment SSZing the transactions too (See EIP-7807)

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

### 1. Fetching Blocks

Fetches beacon blocks using the Beacon API and extracts the execution payload:

```bash
# Fetch last 100 beacon blocks (default)
python fetch_blocks.py
```

The execution payloads from the beacon block is saved to `payloads/` as a JSON file.

You can also fetch the block/payload using a different method and copy it into `payloads/`

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

We use the Beacon API to fetch blocks because it returns execution payloads with RLP encoded transactions. This is what we would expect if they were sent from the CL to the EL via engine API.

Endpoint called:

```text
GET /eth/v2/beacon/blocks/{slot}
```

## Strategies Explained
We have a few variables that we want to play with:

- Tx list encoding
- Compression
- Blob packing

### Transaction List Encoding

Takes `list[bytes]` (raw RLP encoded transactions) and encodes to a single `bytes` blob.

### Compression

Takes encoded bytes and compresses them.

### Blob Packing

Takes compressed bytes and packs into ~128KB blobs. Each blob has 4096 field elements of 32 bytes, but the BLS12-381 scalar field modulus (~2^255) limits usable bits per element.

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
class MyPacker:

    def pack(self, data: bytes) -> list[bytes]:
        ...

    def unpack(self, blobs: list[bytes]) -> bytes:
        ...
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
        ...

    def decode(self, data: bytes) -> list[bytes]:
        ...
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