import unittest

import numpy as np

import simon


class TestSimon(unittest.TestCase):
    def test_invert(self):
        word = np.uint64(0b1010_1100_1111_0000)

        self.assertEqual(simon.invert(word, 16), np.uint64(0b0101_0011_0000_1111))
        self.assertEqual(
            simon.invert(word, 24), np.uint64(0b1111_1111_0101_0011_0000_1111)
        )
        self.assertEqual(
            simon.invert(word, 32), np.uint64(0b1111_1111_1111_1111_0101_0011_0000_1111)
        )
        self.assertEqual(
            simon.invert(word, 48),
            np.uint64(0b1111_1111_1111_1111_1111_1111_1111_1111_0101_0011_0000_1111),
        )
        self.assertEqual(
            simon.invert(word, 64),
            np.uint64(
                0b1111_1111_1111_1111_1111_1111_1111_1111_1111_1111_1111_1111_0101_0011_0000_1111
            ),
        )

        for n in [16, 24, 32, 48, 64]:
            for bits in range(-n + 1, n):
                rotated = simon.rotate_left(word, bits, n)
                inverted = simon.rotate_left(rotated, -bits, n)
                self.assertEqual(inverted, word)

    def test_clean_input(self):
        word1 = np.uint64(0xFFFF_FFFF_FFFF_FFFF)
        word2 = np.uint64(0x1234_5678_9ABC_DEF0)

        input = np.array([word1, word2], dtype=np.uint64)

        np.testing.assert_array_equal(
            simon.clean_input(input, 16),
            np.array([0x0000_0000_0000_FFFF, 0x0000_0000_0000_DEF0], dtype=np.uint64),
        )
        np.testing.assert_array_equal(
            simon.clean_input(input, 24),
            np.array([0x0000_0000_00FF_FFFF, 0x0000_0000_00BC_DEF0], dtype=np.uint64),
        )
        np.testing.assert_array_equal(
            simon.clean_input(input, 32),
            np.array([0x0000_0000_FFFF_FFFF, 0x0000_0000_9ABC_DEF0], dtype=np.uint64),
        )
        np.testing.assert_array_equal(
            simon.clean_input(input, 48),
            np.array([0x0000_FFFF_FFFF_FFFF, 0x0000_5678_9ABC_DEF0], dtype=np.uint64),
        )
        np.testing.assert_array_equal(
            simon.clean_input(input, 64),
            np.array([0xFFFF_FFFF_FFFF_FFFF, 0x1234_5678_9ABC_DEF0], dtype=np.uint64),
        )

    def test_get_round_constant(self):
        self.assertEqual(simon.get_round_constant(0, 0), np.uint64(1))
        self.assertEqual(simon.get_round_constant(0, 5), np.uint64(0))

        self.assertEqual(simon.get_round_constant(0, 62), np.uint64(1))
        self.assertEqual(simon.get_round_constant(0, 67), np.uint64(0))

        self.assertEqual(simon.get_round_constant(1, 5), np.uint64(1))
        self.assertEqual(simon.get_round_constant(1, 67), np.uint64(1))

    def test_rotate(self):
        word = np.uint64(0b0001_0010_0011_0100)

        rotated_left_4 = simon.rotate_left(word, 4, 16)
        expected_left_4 = np.uint64(0b0010_0011_0100_0001)
        self.assertEqual(rotated_left_4, expected_left_4)

        rotated_right_4 = simon.rotate_left(word, -4, 16)
        expected_right_4 = np.uint64(0b0100_0001_0010_0011)
        self.assertEqual(rotated_right_4, expected_right_4)

        rotated_left_4 = simon.rotate_left(word, 4, 24)
        expected_left_4 = np.uint64(0b0000_0001_0010_0011_0100_0000)
        self.assertEqual(rotated_left_4, expected_left_4)

        rotated_right_4 = simon.rotate_left(word, -4, 24)
        expected_right_4 = np.uint64(0b0100_0000_0000_0001_0010_0011)
        self.assertEqual(rotated_right_4, expected_right_4)

        rotated_left_4 = simon.rotate_left(word, 4, 64)
        expected_left_4 = np.uint64(
            0b0000_0000_0000_0000_0000_0000_0000_0000_0000_0000_0000_0001_0010_0011_0100_0000
        )
        self.assertEqual(rotated_left_4, expected_left_4)

        rotated_right_4 = simon.rotate_left(word, -4, 64)
        expected_right_4 = np.uint64(
            0b0100_0000_0000_0000_0000_0000_0000_0000_0000_0000_0000_0000_0000_0001_0010_0011
        )
        self.assertEqual(rotated_right_4, expected_right_4)

    def test_encrypt_simon_32_64(self):
        algo = simon.SIMON_32_64
        key = np.array([0x1918, 0x1110, 0x0908, 0x0100], dtype=np.uint64)
        plaintext = np.array([0x6565, 0x6877], dtype=np.uint64)
        expected_ciphertext = np.array([0xC69B, 0xE9BB], dtype=np.uint64)

        ciphertext = simon.encrypt_block(algo, plaintext, key)
        np.testing.assert_array_equal(ciphertext, expected_ciphertext)
