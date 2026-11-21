"""Byte-oriented Huffman compression for UTF-8 text files.

The archive stores a small JSON header (frequency table and original byte
length) followed by a bit-packed payload. The format is intentionally simple
and self-contained for an algorithms capstone demonstration.
"""

from __future__ import annotations

import argparse
import csv
import heapq
import json
import struct
import statistics
import sys
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

MAGIC = b"HUF1"
HEADER_SIZE = 4


@dataclass
class Node:
    frequency: int
    symbol: Optional[int] = None
    left: Optional["Node"] = None
    right: Optional["Node"] = None


def build_tree(frequencies: dict[int, int]) -> Optional[Node]:
    """Build a deterministic Huffman tree in O(k log k), k=unique bytes."""
    heap: list[tuple[int, int, Node]] = []
    order = 0
    for symbol, frequency in sorted(frequencies.items()):
        heapq.heappush(heap, (frequency, order, Node(frequency, symbol)))
        order += 1
    if not heap:
        return None
    if len(heap) == 1:
        return heap[0][2]
    while len(heap) > 1:
        f1, _, left = heapq.heappop(heap)
        f2, _, right = heapq.heappop(heap)
        parent = Node(f1 + f2, left=left, right=right)
        heapq.heappush(heap, (parent.frequency, order, parent))
        order += 1
    return heap[0][2]


def make_codes(root: Optional[Node]) -> dict[int, str]:
    """Return prefix-free bit strings; a one-symbol input uses code '0'."""
    if root is None:
        return {}
    if root.symbol is not None:
        return {root.symbol: "0"}
    codes: dict[int, str] = {}

    def walk(node: Node, prefix: str) -> None:
        if node.symbol is not None:
            codes[node.symbol] = prefix
            return
        assert node.left is not None and node.right is not None
        walk(node.left, prefix + "0")
        walk(node.right, prefix + "1")

    walk(root, "")
    return codes


def encode_bytes(data: bytes) -> bytes:
    """Encode bytes to the HUF1 container format."""
    frequencies = Counter(data)
    root = build_tree(dict(frequencies))
    codes = make_codes(root)
    header = json.dumps(
        {"length": len(data), "frequencies": {str(k): v for k, v in sorted(frequencies.items())}},
        separators=(",", ":"),
    ).encode("ascii")
    payload = bytearray()
    current = 0
    bit_count = 0
    for symbol in data:
        for bit in codes[symbol]:
            current = (current << 1) | (bit == "1")
            bit_count += 1
            if bit_count == 8:
                payload.append(current)
                current = 0
                bit_count = 0
    if bit_count:
        payload.append(current << (8 - bit_count))
    return MAGIC + struct.pack(">I", len(header)) + header + bytes(payload)


def decode_bytes(archive: bytes) -> bytes:
    """Validate and decode a HUF1 container."""
    if len(archive) < HEADER_SIZE + 4 or archive[:4] != MAGIC:
        raise ValueError("Not a valid HUF1 archive")
    header_len = struct.unpack(">I", archive[4:8])[0]
    if header_len > len(archive) - 8:
        raise ValueError("Truncated archive header")
    try:
        metadata = json.loads(archive[8:8 + header_len].decode("ascii"))
        expected = int(metadata["length"])
        frequencies = {int(k): int(v) for k, v in metadata["frequencies"].items()}
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid archive metadata") from exc
    if expected < 0 or any(k < 0 or k > 255 or v <= 0 for k, v in frequencies.items()):
        raise ValueError("Invalid frequency table")
    if sum(frequencies.values()) != expected:
        raise ValueError("Frequency total does not match original length")
    if expected == 0:
        if frequencies or len(archive) != 8 + header_len:
            raise ValueError("Invalid empty archive")
        return b""
    if not frequencies:
        raise ValueError("Missing frequency table")
    root = build_tree(frequencies)
    payload = archive[8 + header_len:]
    out = bytearray()
    if root is not None and root.symbol is not None:
        if len(payload) < (expected + 7) // 8:
            raise ValueError("Truncated payload")
        return bytes([root.symbol]) * expected
    assert root is not None
    node = root
    for packed in payload:
        for shift in range(7, -1, -1):
            node = node.right if ((packed >> shift) & 1) else node.left  # type: ignore[assignment]
            if node is None:
                raise ValueError("Invalid encoded bit sequence")
            if node.symbol is not None:
                out.append(node.symbol)
                if len(out) == expected:
                    if Counter(out) != Counter(frequencies):
                        raise ValueError("Decoded frequencies do not match archive metadata")
                    return bytes(out)
                node = root
    raise ValueError("Truncated payload")


def compress_file(source: Path, destination: Path) -> dict[str, float | int]:
    original = source.read_bytes()
    start = time.perf_counter()
    archive = encode_bytes(original)
    elapsed = time.perf_counter() - start
    destination.write_bytes(archive)
    return {"original_bytes": len(original), "archive_bytes": len(archive),
            "ratio": len(archive) / len(original) if original else 0.0,
            "space_saved_percent": (1 - len(archive) / len(original)) * 100 if original else 0.0,
            "encode_seconds": elapsed}


def decompress_file(source: Path, destination: Path) -> int:
    decoded = decode_bytes(source.read_bytes())
    destination.write_bytes(decoded)
    return len(decoded)


def run_benchmark(repeats: int = 7) -> list[dict[str, str | int | float]]:
    """Compare size and median encoding time on six reproducible byte inputs."""
    import random

    rng = random.Random(2026)
    cases = [
        ("repeated_pattern_4k", (b"ABRACADABRA! " * 316)[:4096]),
        ("english_like_4k", (b"the quick brown fox jumps over the lazy dog. " * 100)[:4096]),
        ("uniform_bytes_4k", bytes(rng.randrange(256) for _ in range(4096))),
        ("repeated_pattern_64k", (b"ABRACADABRA! " * 5042)[:65536]),
        ("english_like_64k", (b"the quick brown fox jumps over the lazy dog. " * 2000)[:65536]),
        ("uniform_bytes_64k", bytes(rng.randrange(256) for _ in range(65536))),
    ]
    results = []
    for name, data in cases:
        samples = []
        archive = b""
        for _ in range(repeats):
            start = time.perf_counter()
            archive = encode_bytes(data)
            samples.append(time.perf_counter() - start)
        results.append({
            "input": name,
            "input_bytes": len(data),
            "distinct_bytes": len(set(data)),
            "archive_bytes": len(archive),
            "ratio": round(len(archive) / len(data), 4),
            "median_encode_ms": round(statistics.median(samples) * 1000, 3),
            "repeats": repeats,
        })
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Compress or decompress using Huffman coding.")
    commands = parser.add_subparsers(dest="command", required=True)
    comp = commands.add_parser("compress", help="compress a text or binary file")
    comp.add_argument("input", type=Path)
    comp.add_argument("output", type=Path)
    decomp = commands.add_parser("decompress", help="restore a HUF1 archive")
    decomp.add_argument("input", type=Path)
    decomp.add_argument("output", type=Path)
    bench = commands.add_parser("benchmark", help="compare compression size and speed on sample data")
    bench.add_argument("--repeats", type=int, default=7)
    bench.add_argument("--csv", type=Path, help="optional path for saving results as CSV")
    args = parser.parse_args()
    if args.command == "compress":
        stats = compress_file(args.input, args.output)
        print(f"Original: {stats['original_bytes']} bytes")
        print(f"Archive:  {stats['archive_bytes']} bytes")
        print(f"Ratio:    {stats['ratio']:.3f}")
        print(f"Saved:    {stats['space_saved_percent']:.2f}%")
        print(f"Encode:   {stats['encode_seconds']:.6f} seconds")
    elif args.command == "decompress":
        restored = decompress_file(args.input, args.output)
        print(f"Restored {restored} bytes to {args.output}")
    else:
        if args.repeats < 1:
            parser.error("--repeats must be at least 1")
        rows = run_benchmark(args.repeats)
        if args.csv:
            with args.csv.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
        writer = csv.DictWriter(sys.stdout, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
