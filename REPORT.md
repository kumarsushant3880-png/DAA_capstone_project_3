# Huffman Coding for File Compression

## Capstone Project Report

**Project area:** Data structures, greedy algorithms, and data analysis  
**Student:** Sushant Kumar  
**Roll number:** 2501010290  
**Course:** B.Tech CSE Core  
**Subject:** Design and Analysis of Algorithms (DAA)  
**Teacher:** Anvi Aggrawal  
**Submission date:** 20 November 2026

## Abstract

This project implements lossless file compression using Huffman coding. It counts byte frequencies, builds a binary Huffman tree with a min-priority queue, assigns a prefix-free binary code to each distinct byte, and packs those codes into an archive. A decoder rebuilds the tree from archive metadata and restores the original bytes. A deterministic experiment measures archive size and median encoding time on repeated text, English-like text, and uniformly distributed bytes at two input sizes. Results show that compression depends on the frequency distribution: skewed data compresses well, while uniform data may grow after metadata is added. Five automated checks verify round trips and edge cases.

## 1. Problem Statement

Text files can contain repeated symbols, and storing every symbol with a fixed-width code can use more bits than necessary. This project demonstrates how variable-length, prefix-free codes reduce the representation size when some symbols occur more often than others.

The project counts byte frequencies, constructs a Huffman tree, generates binary codes, encodes and decodes files without information loss, compares file sizes across data patterns, and analyzes the algorithms' time and space complexity.

## 2. Objectives

- Calculate byte frequencies from an input file.
- Construct a Huffman tree and generate prefix-free codes.
- Encode and decode files without losing information.
- Compare original and archive sizes across different input patterns.
- Describe time and space complexity and the limits of the method.

## 3. Tools and Requirements

The program is written in Python 3.10 or newer and uses only the Python standard library. It uses a min-heap priority queue (`heapq`) to build the Huffman tree. No package installation is required.

## 4. Methodology

The program reads files as bytes. This supports UTF-8 text and also preserves arbitrary byte values without changing the compression algorithm. For each byte, the encoder counts occurrences and inserts one leaf per distinct byte into a min-heap. It repeatedly removes the two nodes with the smallest frequencies and joins them under a parent node with the summed frequency. The final tree determines codewords: a left edge contributes `0`, and a right edge contributes `1`.

The encoder substitutes each byte with its code and packs the resulting bits into output bytes. The archive starts with a `HUF1` signature, followed by a length field and a JSON header containing the original size and byte-frequency table. The packed payload follows. The decoder reads the header, reconstructs the same deterministic tree, follows each bit from the root, and emits a byte whenever it reaches a leaf. It stops at the recorded original length and checks decoded frequencies against the header.

An empty input has an empty frequency table and no payload. If the input contains only one distinct byte, that symbol uses code `0`; the recorded size tells the decoder how many copies to restore.

## 5. Algorithm

1. Read the input file and count each byte's occurrences.
2. Add each distinct byte and its frequency to a min-priority queue.
3. Remove the two least-frequent nodes and join them under a parent with their combined frequency.
4. Repeat until one tree remains.
5. Generate each byte's code from its root-to-leaf path, using `0` for left and `1` for right.
6. Replace input bytes with their codes and pack the bits into the archive payload.
7. For decoding, rebuild the tree from saved frequencies, walk it using payload bits, and stop after restoring the original byte count.

Huffman codes are prefix-free: no symbol's code is the beginning of another symbol's code. This property makes decoding unambiguous.

## 6. Complexity Analysis

Let `n` be the number of input bytes and `k` the number of distinct byte values. A byte can have only 256 possible values, so `k <= 256`.

| Stage | Time complexity | Extra space |
|---|---:|---:|
| Frequency counting | `O(n)` | `O(k)` |
| Huffman tree construction | `O(k log k)` | `O(k)` |
| Code generation | `O(k)` | `O(k)` |
| Encoding and decoding | `O(n)` for the bounded byte alphabet | `O(n)` for output buffers |

The program keeps file data and the encoded or decoded result in memory. Overall working space is `O(n + k)`. A streaming implementation could reduce buffer memory, but it would add complexity.

## 7. Experimental Setup

The benchmark builds six deterministic inputs: a repeated pattern, English-like repeated text, and seeded uniformly random bytes at 4 KiB and 64 KiB. It runs each encoding seven times and reports the median duration. Archive size includes the frequency-table header and payload. Timing is an example run on one local environment, not a hardware-independent performance claim. Run `python benchmark.py` to measure another machine.

## 8. Results and Analysis

| Input | Original bytes | Distinct byte values | Archive bytes | Archive / original | Median encode time |
|---|---:|---:|---:|---:|---:|
| Repeated pattern, 4 KiB | 4,096 | 7 | 1,403 | 0.3425 | 1.851 ms |
| English-like text, 4 KiB | 4,096 | 28 | 2,580 | 0.6299 | 2.955 ms |
| Uniform bytes, 4 KiB | 4,096 | 256 | 6,309 | 1.5403 | 6.198 ms |
| Repeated pattern, 64 KiB | 65,536 | 7 | 20,908 | 0.3190 | 30.750 ms |
| English-like text, 64 KiB | 65,536 | 28 | 36,935 | 0.5636 | 43.050 ms |
| Uniform bytes, 64 KiB | 65,536 | 256 | 68,026 | 1.0380 | 83.785 ms |

The ratio is archive bytes divided by original bytes. A value below 1 indicates a smaller archive. In this run, repeated data saved about 66% at 4 KiB and 68% at 64 KiB. English-like text saved about 37% and 44%, respectively. Uniform bytes grew about 54% for the small input and about 4% for the larger one.

Uniform data has little frequency skew, so the encoded payload does not offset the metadata cost. The fixed header is spread across more input bytes at 64 KiB, which explains why the larger uniform archive is closer to its original size. Encoding time increased with input size and amount of bit processing. Small timing differences should be interpreted cautiously because they depend on the computer, operating system, Python version, and background workload.

## 9. Validation

Five automated checks passed:

1. UTF-8 text round-trip, including non-ASCII characters.
2. Empty input round-trip.
3. Single-symbol input and its one-bit code.
4. All 256 byte values repeated four times.
5. Rejection of an archive with an invalid signature.

Run the checks with `python -m unittest -v`. A successful round-trip means decoded output is byte-for-byte equal to the source.

## 10. Conclusion

The implementation counts frequencies, creates a Huffman tree, generates codes, encodes and decodes files, and compares size and runtime across input distributions and sizes. The experiment demonstrates that Huffman compression benefits from uneven symbol frequencies and that archive metadata matters, particularly for small or uniform inputs. The tree-building process also demonstrates the greedy algorithm strategy of combining the two least-frequent nodes at each step.

## 11. Limitations and Future Improvements

This educational archive format is not a replacement for ZIP or gzip. It loads complete files into memory, stores metadata as JSON, and has no checksum or streaming support. Further work could add corruption detection, reduce metadata overhead with a binary header, support streaming, and compare against standard compression tools on a broader set of real files.

## 12. Demonstration Procedure

1. Show `sample.txt` and run the compression command in the README.
2. Compare the original and archive sizes. Explain that header overhead is proportionally larger for small files.
3. Decompress the archive and compare the restored file with the original.
4. Run the unit checks.
5. Show the benchmark table and explain why uniform-byte cases compress poorly.
6. Explain the min-heap, prefix-free property, and complexity analysis.
