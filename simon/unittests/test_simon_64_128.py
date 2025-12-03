import unittest

import numpy as np

import simon_64_128


class TestSimon_64_128(unittest.TestCase):

    def test_simon_64_128(self):
        key = np.array(
            [0x1B1A1918, 0x13121110, 0x0B0A0908, 0x03020100], dtype=np.uint32
        )
        plaintext = np.array([0x656B696C, 0x20646E75], dtype=np.uint32)
        expected_ciphertext = np.array([0x44C8FC20, 0xB9DFA07A], dtype=np.uint32)
        ciphertext, _ = simon_64_128.encrypt_block(plaintext, key)
        np.testing.assert_array_equal(ciphertext, expected_ciphertext)

    def test_get_round_constant(self):
        self.assertEqual(
            simon_64_128.get_round_constant(0), 1
        )
        self.assertEqual(
            simon_64_128.get_round_constant(1), 1
        )
        self.assertEqual(
            simon_64_128.get_round_constant(2), 0
        )
