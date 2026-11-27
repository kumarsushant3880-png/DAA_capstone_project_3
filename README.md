# Huffman File Compression

**Student:** Sushant Kumar · **Roll No.:** 2501010290  
**Course:** B.Tech CSE Core · **Subject:** Design and Analysis of Algorithms (DAA)  
**Teacher:** Anvi Aggrawal

This project implements lossless Huffman coding for files. It counts byte frequencies, builds a Huffman tree with a min-heap, packs variable-length codes into a binary archive, restores the original bytes, and measures compression size and encoding time.

## Project Structure

```text
huffman-file-compression/
├── huffman.py   # Huffman algorithm, file I/O, and benchmark command
├── sample.txt   # Sample text file for immediate testing
└── README.md    # Usage, algorithm, complexity, and results
```

## Requirements

- Python 3.10 or newer
- No third-party packages

## Compress and Decompress

Open the VS Code terminal (**Terminal → New Terminal**) and make sure it is
in this project folder. On Windows, check that Python is available with
`py --version` (Python 3.10 or newer is required). Then run:

```powershell
py huffman.py compress sample.txt sample.huf
py huffman.py decompress sample.huf restored.txt
```

If `py` is not recognized but `python --version` works, replace `py` with
`python` in the commands. If neither command works, install Python 3.10 or
newer from python.org, enable the option to add Python to PATH during setup,
then reopen the terminal.

To check the restored file against the original in PowerShell, run:

```powershell
Get-FileHash sample.txt, restored.txt
```

Compression reports the source size, archive size, compression ratio, space saved, and encoding time. The program processes bytes, so UTF-8 text and arbitrary byte values are preserved. The `.huf` archive contains a `HUF1` signature, a JSON frequency table with the original byte count, and a packed bitstream.

## Benchmark

Run the included reproducible size and timing comparison:

```bash
python huffman.py benchmark
python huffman.py benchmark --repeats 10 --csv results.csv
```

The benchmark compares repeated text, English-like text, and seeded uniformly distributed bytes at 4 KiB and 64 KiB. It reports archive-to-input ratio and median encoding time. A ratio below `1.0` means the archive is smaller. Timing depends on the computer, Python version, and background activity.

### Sample Results

One run of the included deterministic cases produced these measurements. Times are illustrative; rerun the benchmark for timings on your computer.

| Input | Input bytes | Distinct bytes | Archive bytes | Ratio | Median encode time |
|---|---:|---:|---:|---:|---:|
| Repeated pattern, 4 KiB | 4,096 | 7 | 1,403 | 0.3425 | 1.851 ms |
| English-like text, 4 KiB | 4,096 | 28 | 2,580 | 0.6299 | 2.955 ms |
| Uniform bytes, 4 KiB | 4,096 | 256 | 6,309 | 1.5403 | 6.198 ms |
| Repeated pattern, 64 KiB | 65,536 | 7 | 20,908 | 0.3190 | 30.750 ms |
| English-like text, 64 KiB | 65,536 | 28 | 36,935 | 0.5636 | 43.050 ms |
| Uniform bytes, 64 KiB | 65,536 | 256 | 68,026 | 1.0380 | 83.785 ms |

Repeated patterns compress well because frequent bytes receive short codes. Uniform random bytes have little frequency skew, so their encoded bits do not compensate for the frequency-table header; small files can therefore grow.

## How the Algorithm Works

1. Count the occurrences of each input byte.
2. Add each distinct byte to a min-heap ordered by frequency.
3. Repeatedly remove the two least-frequent nodes and join them under a parent whose frequency is their sum.
4. Traverse the completed tree: left edges mean `0`, right edges mean `1`. Each leaf's path is that byte's code.
5. Replace each source byte with its code and pack the bits into output bytes.
6. For decompression, rebuild the tree from the stored frequencies and walk the bits until the original byte count is restored.

The greedy tree-building step combines the two least-frequent nodes each time. Codes are prefix-free because only leaves represent bytes; no byte code is the prefix of another, so decoding is unambiguous.

## Complexity

Let `n` be the number of input bytes and `k` the number of distinct byte values (`k <= 256`). Frequency counting and processing the encoded data take `O(n)` time for this fixed byte alphabet. Tree construction takes `O(k log k)` time using the min-heap. The tree and code table use `O(k)` space. This implementation keeps source and result buffers in memory, for `O(n + k)` working space.

## Code Walkthrough

- `Node` stores a frequency, an optional byte symbol, and child references.
- `build_tree` applies the greedy choice with `heapq`; the order counter makes equal-frequency ties deterministic.
- `make_codes` traverses the tree and assigns a prefix-free bit string to every byte.
- `encode_bytes` writes the frequency metadata and packs code bits into bytes.
- `decode_bytes` validates the archive, recreates the tree, and reconstructs the original data.
- `compress_file` and `decompress_file` provide the file interface. The `benchmark` command measures size ratios and median encoder runtime.

## Scope

This is a teaching format, not a replacement for ZIP or gzip. It is lossless, but compression is not guaranteed for every file. The archive has no checksum, encryption, or streaming support. Use established archive software for important data.
