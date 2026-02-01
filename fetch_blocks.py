#!/usr/bin/env python3
"""Fetch blocks via Beacon API (execution payload with raw transactions)."""

import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import click

DEFAULT_BEACON = "https://ethereum-beacon-api.publicnode.com"


def beacon_get(url: str, timeout: int = 30) -> dict:
    """Make a Beacon API GET request."""
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "blob-experiments"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def fetch_block(beacon_url: str, slot: int | str) -> dict | None:
    """Fetch a block and extract execution payload."""
    try:
        url = f"{beacon_url}/eth/v2/beacon/blocks/{slot}"
        data = beacon_get(url)

        block = data["data"]["message"]
        exec_payload = block["body"]["execution_payload"]

        return exec_payload
    except Exception as e:
        print(f"  Error fetching slot {slot}: {e}")
        return None


def get_head_slot(beacon_url: str) -> int:
    """Get the current head slot."""
    data = beacon_get(f"{beacon_url}/eth/v1/beacon/headers/head")
    return int(data["data"]["header"]["message"]["slot"])


@click.command()
@click.option("--start", "-s", type=int, default=None, help="Start slot")
@click.option("--end", "-e", type=int, default=None, help="End slot")
@click.option("--count", "-c", type=int, default=100, help="Number of slots (default: 100)")
@click.option(
    "--beacon", "-b", default=DEFAULT_BEACON, envvar="BEACON_URL", help="Beacon API URL"
)
@click.option(
    "--output-dir", "-o", type=click.Path(path_type=Path), default="payloads", help="Output directory"
)
@click.option("--workers", "-w", type=int, default=5, help="Parallel workers (default: 5)")
def main(start: int | None, end: int | None, count: int, beacon: str, output_dir: Path, workers: int):
    """Fetch blocks via Beacon API (1 call per block, raw transactions included).

    Examples:
      python fetch_blocks.py              # Last 100 slots
      python fetch_blocks.py -c 50        # Last 50 slots
      python fetch_blocks.py -s 9000000   # From specific slot
    """
    print(f"Using Beacon API: {beacon}")

    if end is None:
        end = get_head_slot(beacon)
        print(f"Head slot: {end}")

    if start is None:
        start = end - count + 1

    slots = list(range(start, end + 1))
    print(f"Fetching {len(slots)} slots: {start} to {end}")

    output_dir.mkdir(parents=True, exist_ok=True)

    completed = 0
    failed = 0
    skipped = 0

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(fetch_block, beacon, s): s for s in slots}

        for future in as_completed(futures):
            slot = futures[future]
            try:
                payload = future.result()
                if payload:
                    block_num = int(payload["block_number"])
                    output_path = output_dir / f"block_{block_num}.json"
                    with open(output_path, "w") as f:
                        json.dump(payload, f)
                    tx_count = len(payload["transactions"])
                    completed += 1
                    print(f"[{completed}/{len(slots)}] Slot {slot} (block {block_num}): {tx_count} txs")
                else:
                    # Slot might be empty (missed block)
                    skipped += 1
            except Exception as e:
                failed += 1
                print(f"Slot {slot}: ERROR - {e}")

    print(f"\nDone! Fetched {completed} blocks, {skipped} empty slots, {failed} failed")
    print(f"Saved to {output_dir}/")


if __name__ == "__main__":
    main()
