"""Small self-check suite; run with: python -m unittest -v"""
import unittest

from huffman import decode_bytes, encode_bytes, make_codes, build_tree


class HuffmanTests(unittest.TestCase):
    def test_round_trip_text(self):
        data = "Huffman coding compresses repeated symbols. नमस्ते 🌍".encode("utf-8")
        self.assertEqual(decode_bytes(encode_bytes(data)), data)

    def test_empty_input(self):
        self.assertEqual(decode_bytes(encode_bytes(b"")), b"")

    def test_single_symbol(self):
        data = b"z" * 101
        self.assertEqual(decode_bytes(encode_bytes(data)), data)
        self.assertEqual(make_codes(build_tree({ord("z"): 101})), {ord("z"): "0"})

    def test_all_byte_values(self):
        data = bytes(range(256)) * 4
        self.assertEqual(decode_bytes(encode_bytes(data)), data)

    def test_reject_bad_magic(self):
        with self.assertRaises(ValueError):
            decode_bytes(b"NOPE" + b"\0" * 20)


if __name__ == "__main__":
    unittest.main()
