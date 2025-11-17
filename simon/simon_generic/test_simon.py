import unittest

import numpy as np

import simon_generic.simon as simon


class TestSimon(unittest.TestCase):
    def test_expand_key_alt(self):
        """No test vectors are available for key expansion, so checking two alternative implementations
        give the same result. Additionally, the first implementation is implicitly tested through the encryption tests.
        """
        for algo in [
            simon.SIMON_32_64,
            simon.SIMON_48_72,
            simon.SIMON_48_96,
            simon.SIMON_64_96,
            simon.SIMON_64_128,
            simon.SIMON_96_96,
            simon.SIMON_96_144,
            simon.SIMON_128_128,
            simon.SIMON_128_192,
            simon.SIMON_128_256,
        ]:
            for _ in range(10):
                key = np.random.randint(0, 2**algo.n, size=(algo.m,), dtype=np.uint64)

                expanded_key = simon.expand_key(algo, key)
                expanded_key_alt = simon.expand_key_alt(algo, key)

                np.testing.assert_array_equal(expanded_key, expanded_key_alt)

    def test_invert(self):
        word = np.uint64(0b1010_1100_1111_0000)

        self.assertEqual(
            simon.invert(word, simon.SIMON_32_64), np.uint64(0b0101_0011_0000_1111)
        )
        self.assertEqual(
            simon.invert(word, simon.SIMON_48_72),
            np.uint64(0b1111_1111_0101_0011_0000_1111),
        )
        self.assertEqual(
            simon.invert(word, simon.SIMON_64_96),
            np.uint64(0b1111_1111_1111_1111_0101_0011_0000_1111),
        )
        self.assertEqual(
            simon.invert(word, simon.SIMON_96_144),
            np.uint64(0b1111_1111_1111_1111_1111_1111_1111_1111_0101_0011_0000_1111),
        )
        self.assertEqual(
            simon.invert(word, simon.SIMON_128_128),
            np.uint64(
                0b1111_1111_1111_1111_1111_1111_1111_1111_1111_1111_1111_1111_0101_0011_0000_1111
            ),
        )

        for algo in [
            simon.SIMON_32_64,
            simon.SIMON_48_72,
            simon.SIMON_64_96,
            simon.SIMON_96_144,
            simon.SIMON_128_128,
        ]:
            for bits in range(-algo.n + 1, algo.n):
                rotated = simon.rotate_left(word, bits, algo)
                inverted = simon.rotate_left(rotated, -bits, algo)
                self.assertEqual(inverted, word)

    def test_clean_input(self):
        word1 = np.uint64(0xFFFF_FFFF_FFFF_FFFF)
        word2 = np.uint64(0x1234_5678_9ABC_DEF0)

        input = np.array([word1, word2], dtype=np.uint64)

        np.testing.assert_array_equal(
            simon.clean_input(input, simon.SIMON_32_64),
            np.array([0x0000_0000_0000_FFFF, 0x0000_0000_0000_DEF0], dtype=np.uint64),
        )
        np.testing.assert_array_equal(
            simon.clean_input(input, simon.SIMON_48_72),
            np.array([0x0000_0000_00FF_FFFF, 0x0000_0000_00BC_DEF0], dtype=np.uint64),
        )
        np.testing.assert_array_equal(
            simon.clean_input(input, simon.SIMON_64_96),
            np.array([0x0000_0000_FFFF_FFFF, 0x0000_0000_9ABC_DEF0], dtype=np.uint64),
        )
        np.testing.assert_array_equal(
            simon.clean_input(input, simon.SIMON_96_96),
            np.array([0x0000_FFFF_FFFF_FFFF, 0x0000_5678_9ABC_DEF0], dtype=np.uint64),
        )
        np.testing.assert_array_equal(
            simon.clean_input(input, simon.SIMON_128_128),
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

        rotated_left_4 = simon.rotate_left(word, 4, simon.SIMON_32_64)
        expected_left_4 = np.uint64(0b0010_0011_0100_0001)
        self.assertEqual(rotated_left_4, expected_left_4)

        rotated_right_4 = simon.rotate_left(word, -4, simon.SIMON_32_64)
        expected_right_4 = np.uint64(0b0100_0001_0010_0011)
        self.assertEqual(rotated_right_4, expected_right_4)

        rotated_left_4 = simon.rotate_left(word, 4, simon.SIMON_48_72)
        expected_left_4 = np.uint64(0b0000_0001_0010_0011_0100_0000)
        self.assertEqual(rotated_left_4, expected_left_4)

        rotated_right_4 = simon.rotate_left(word, -4, simon.SIMON_48_72)
        expected_right_4 = np.uint64(0b0100_0000_0000_0001_0010_0011)
        self.assertEqual(rotated_right_4, expected_right_4)

        rotated_left_4 = simon.rotate_left(word, 4, simon.SIMON_128_256)
        expected_left_4 = np.uint64(
            0b0000_0000_0000_0000_0000_0000_0000_0000_0000_0000_0000_0001_0010_0011_0100_0000
        )
        self.assertEqual(rotated_left_4, expected_left_4)

        rotated_right_4 = simon.rotate_left(word, -4, simon.SIMON_128_256)
        expected_right_4 = np.uint64(
            0b0100_0000_0000_0000_0000_0000_0000_0000_0000_0000_0000_0000_0000_0001_0010_0011
        )
        self.assertEqual(rotated_right_4, expected_right_4)

    def test_simon_32_64(self):
        algo = simon.SIMON_32_64
        key = np.array([0x1918, 0x1110, 0x0908, 0x0100], dtype=np.uint64)
        plaintext = np.array([0x6565, 0x6877], dtype=np.uint64)
        expected_ciphertext = np.array([0xC69B, 0xE9BB], dtype=np.uint64)
        ciphertext = simon.encrypt_block(algo, plaintext, key)
        np.testing.assert_array_equal(ciphertext, expected_ciphertext)

    def test_simon_48_72(self):
        algo = simon.SIMON_48_72
        key = np.array([0x121110, 0x0A0908, 0x020100], dtype=np.uint64)
        plaintext = np.array([0x612067, 0x6E696C], dtype=np.uint64)
        expected_ciphertext = np.array([0xDAE5AC, 0x292CAC], dtype=np.uint64)
        ciphertext = simon.encrypt_block(algo, plaintext, key)
        np.testing.assert_array_equal(ciphertext, expected_ciphertext)

    def test_simon_48_96(self):
        algo = simon.SIMON_48_96
        key = np.array([0x1A1918, 0x121110, 0x0A0908, 0x020100], dtype=np.uint64)
        plaintext = np.array([0x726963, 0x20646E], dtype=np.uint64)
        expected_ciphertext = np.array([0x6E06A5, 0xACF156], dtype=np.uint64)
        ciphertext = simon.encrypt_block(algo, plaintext, key)
        np.testing.assert_array_equal(ciphertext, expected_ciphertext)

    def test_simon_64_96(self):
        algo = simon.SIMON_64_96
        key = np.array([0x13121110, 0x0B0A0908, 0x03020100], dtype=np.uint64)
        plaintext = np.array([0x6F722067, 0x6E696C63], dtype=np.uint64)
        expected_ciphertext = np.array([0x5CA2E27F, 0x111A8FC8], dtype=np.uint64)
        ciphertext = simon.encrypt_block(algo, plaintext, key)
        np.testing.assert_array_equal(ciphertext, expected_ciphertext)

    def test_simon_64_128(self):
        algo = simon.SIMON_64_128
        key = np.array(
            [0x1B1A1918, 0x13121110, 0x0B0A0908, 0x03020100], dtype=np.uint64
        )
        plaintext = np.array([0x656B696C, 0x20646E75], dtype=np.uint64)
        expected_ciphertext = np.array([0x44C8FC20, 0xB9DFA07A], dtype=np.uint64)
        ciphertext = simon.encrypt_block(algo, plaintext, key)
        np.testing.assert_array_equal(ciphertext, expected_ciphertext)

    def test_simon_96_96(self):
        algo = simon.SIMON_96_96
        key = np.array([0x0D0C0B0A0908, 0x050403020100], dtype=np.uint64)
        plaintext = np.array([0x2072616C6C69, 0x702065687420], dtype=np.uint64)
        expected_ciphertext = np.array(
            [0x602807A462B4, 0x69063D8FF082], dtype=np.uint64
        )
        ciphertext = simon.encrypt_block(algo, plaintext, key)
        np.testing.assert_array_equal(ciphertext, expected_ciphertext)

    def test_simon_96_144(self):
        algo = simon.SIMON_96_144
        key = np.array(
            [0x151413121110, 0x0D0C0B0A0908, 0x050403020100], dtype=np.uint64
        )
        plaintext = np.array([0x746168742074, 0x73756420666F], dtype=np.uint64)
        expected_ciphertext = np.array(
            [0xECAD1C6C451E, 0x3F59C5DB1AE9], dtype=np.uint64
        )
        ciphertext = simon.encrypt_block(algo, plaintext, key)
        np.testing.assert_array_equal(ciphertext, expected_ciphertext)

    def test_simon_128_128(self):
        algo = simon.SIMON_128_128
        key = np.array([0x0F0E0D0C0B0A0908, 0x0706050403020100], dtype=np.uint64)
        plaintext = np.array([0x6373656420737265, 0x6C6C657661727420], dtype=np.uint64)
        expected_ciphertext = np.array(
            [0x49681B1E1E54FE3F, 0x65AA832AF84E0BBC], dtype=np.uint64
        )
        ciphertext = simon.encrypt_block(algo, plaintext, key)
        np.testing.assert_array_equal(ciphertext, expected_ciphertext)

    def test_simon_128_192(self):
        algo = simon.SIMON_128_192
        key = np.array(
            [0x1716151413121110, 0x0F0E0D0C0B0A0908, 0x0706050403020100],
            dtype=np.uint64,
        )
        plaintext = np.array([0x206572656874206E, 0x6568772065626972], dtype=np.uint64)
        expected_ciphertext = np.array(
            [0xC4AC61EFFCDC0D4F, 0x6C9C8D6E2597B85B], dtype=np.uint64
        )
        ciphertext = simon.encrypt_block(algo, plaintext, key)
        np.testing.assert_array_equal(ciphertext, expected_ciphertext)

    def test_simon_128_256(self):
        algo = simon.SIMON_128_256
        key = np.array(
            [
                0x1F1E1D1C1B1A1918,
                0x1716151413121110,
                0x0F0E0D0C0B0A0908,
                0x0706050403020100,
            ],
            dtype=np.uint64,
        )
        plaintext = np.array([0x74206E69206D6F6F, 0x6D69732061207369], dtype=np.uint64)
        expected_ciphertext = np.array(
            [0x8D2B5579AFC8A3A0, 0x3BF72A87EFE7B868], dtype=np.uint64
        )
        ciphertext = simon.encrypt_block(algo, plaintext, key)
        np.testing.assert_array_equal(ciphertext, expected_ciphertext)
