# Huffman File Compression

A small Python capstone project that compresses files with Huffman coding and restores them exactly. It demonstrates frequency counting, priority-queue tree construction, prefix codes, bit packing, decoding, file-size analysis, and basic runtime experiments.

## Run it

Requires Python 3.10 or newer. No third-party packages are needed.

```bash
python huffman.py compress sample.txt sample.huf
python huffman.py decompress sample.huf restored.txt
```

The encoder accepts any file, including UTF-8 text. Compression works on the file's bytes so every input byte is preserved. The output is a custom `HUF1` archive containing a JSON frequency table and the packed bitstream. Keep the `.huf` file with its original header; the decoder needs the frequency table to rebuild the tree.

## Run the checks and experiment

```bash
python -m unittest -v
python benchmark.py
```

The benchmark uses six deterministic synthetic inputs, seven repeats per case, and reports the median encoding time. Its CSV is included as a sample run; timings vary with the computer and Python version. Run it again to measure your own machine.

## What the algorithm does

1. Count each byte's occurrences.
2. Put each distinct byte into a min-priority queue, ordered by frequency.
3. Repeatedly remove the two least-frequent nodes and join them under a parent whose frequency is their sum.
4. Read left edges as `0` and right edges as `1`; each leaf's root-to-leaf path is its code.
5. Replace each input byte with its code and pack bits into output bytes.
6. During decompression, rebuild the same tree from the frequency table and walk it one bit at a time. Stop after the original byte count is restored.

Common bytes tend to receive shorter codes. Huffman codes are prefix-free, so no code is the beginning of another code; this makes the bitstream unambiguous.

## Complexity

Let `n` be the number of input bytes and `k` the number of distinct byte values (`k <= 256`). Counting and encoding/decoding take `O(n)` time for this byte alphabet. Building the tree takes `O(k log k)` time and `O(k)` extra space. The code table and tree use `O(k)` space; the implementation also keeps the input and output buffers in memory, so total working memory is `O(n + k)`. The archive header adds metadata overhead, which is why tiny files may grow.

## Important result to explain

Huffman coding is lossless but does not guarantee that every input shrinks. The included benchmark shows that repeated and English-like inputs compress well, while uniformly distributed bytes may stay similar in size or grow because the frequency table and archive header cost space. This is an expected limitation, not a decoding error.

## Viva preparation

**Why does a min-heap help?** It efficiently selects the two smallest frequencies at every tree-building step; insertion and removal take `O(log k)`.

**Why are codes unambiguous?** A Huffman tree assigns codes only to leaves. No leaf is an ancestor of another leaf, so no symbol's code is a prefix of another symbol's code.

**Why can output be larger?** The encoded bits may not save enough space to cover the frequency table and container header. Uniform data has little frequency skew to exploit.

**How do you know decompression is correct?** The decoder restores exactly the recorded input length and checks that the decoded symbol counts match the stored frequency table. Tests also check byte-for-byte round trips.

**What is the key tradeoff?** Huffman coding finds optimal prefix-code lengths for the known symbol frequencies, but the decoder needs those frequencies (or an equivalent tree) stored with the compressed data.

## Archive format and limitations

The format is for teaching and is not a replacement for ZIP, gzip, or production archivers. It uses a four-byte `HUF1` signature, a four-byte big-endian header length, a JSON header with original length and byte frequencies, and a byte-aligned bit payload. Unused bits at the end of the last payload byte are zero padding. The original length tells the decoder when to stop. There is no checksum, encryption, streaming mode, or protection against all hostile inputs; use established archive formats for important data.

## Project contents

- `huffman.py` — compressor, decompressor, tree construction, and code generation.
- `test_huffman.py` — correctness and edge-case checks.
- `benchmark.py` — repeatable size and timing experiment.
- `benchmark_results.csv` — sample results from the included deterministic inputs.
- `sample.txt` — small file for a quick demonstration.
- `REPORT.md` — project report and oral explanation.

## Student details

- **Student:** Sushant Kumar
- **Roll number:** 2501010290
- **Course:** B.Tech CSE Core
- **Subject:** Design and Analysis of Algorithms (DAA)
- **Teacher:** Anvi Aggrawal

