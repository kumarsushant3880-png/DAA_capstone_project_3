"""Reproducible Huffman size and timing experiment; uses only Python's stdlib."""
from __future__ import annotations

import csv
import random
import statistics
import time
from pathlib import Path

from huffman import encode_bytes


def measure(label: str, data: bytes, repeats: int = 7) -> dict[str, object]:
    samples = []
    archive = b""
    for _ in range(repeats):
        start = time.perf_counter()
        archive = encode_bytes(data)
        samples.append(time.perf_counter() - start)
    return {
        "input": label,
        "input_bytes": len(data),
        "distinct_bytes": len(set(data)),
        "archive_bytes": len(archive),
        "ratio": round(len(archive) / len(data), 4) if data else 0,
        "median_encode_ms": round(statistics.median(samples) * 1000, 3),
        "repeats": repeats,
    }


def main() -> None:
    out = Path(__file__).with_name("benchmark_results.csv")
    rng = random.Random(2026)
    cases = [
        ("repeated_pattern_4k", (b"ABRACADABRA! " * 316)[:4096]),
        ("english_like_4k", ((b"the quick brown fox jumps over the lazy dog. " * 100)[:4096])),
        ("uniform_bytes_4k", bytes(rng.randrange(256) for _ in range(4096))),
        ("repeated_pattern_64k", (b"ABRACADABRA! " * 5042)[:65536]),
        ("english_like_64k", ((b"the quick brown fox jumps over the lazy dog. " * 2000)[:65536])),
        ("uniform_bytes_64k", bytes(rng.randrange(256) for _ in range(65536))),
    ]
    rows = [measure(label, data) for label, data in cases]
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {out.name}")
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
