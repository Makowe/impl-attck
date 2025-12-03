import unittest

import numpy as np

import simon_64_128_simulation


class TestSimon_64_128_Simulation(unittest.TestCase):
    def test_get_x_after_round(self):
        key = np.array(
            [0x1B1A1918, 0x13121110, 0x0B0A0908, 0x03020100], dtype=np.uint32
        )
        plaintext = np.array([0x656B696C, 0x20646E75], dtype=np.uint32)

        x_after_round_0 = simon_64_128_simulation.get_x_after_round(
            plaintext, key, 0
        )
        np.testing.assert_array_equal(x_after_round_0, np.array([0xFC8B8A84], dtype=np.uint32))

        x_after_round_1 = simon_64_128_simulation.get_x_after_round(
            plaintext, key, 1
        )
        np.testing.assert_array_equal(x_after_round_1, np.array([0x154D4E7F], dtype=np.uint32))

        x_after_round_2 = simon_64_128_simulation.get_x_after_round(
            plaintext, key, 2
        )
        np.testing.assert_array_equal(x_after_round_2, np.array([0xB2A6BE7C], dtype=np.uint32))

        x_after_round_3 = simon_64_128_simulation.get_x_after_round(
            plaintext, key, 3
        )
        np.testing.assert_array_equal(x_after_round_3, np.array([0xE0C1D225], dtype=np.uint32))

    def test_get_hws_for_guessed_key_byte(self):
        plaintexts = np.array(
            [
                [0x656B696C, 0x20646E75],
                [0x12345678, 0x9ABCDEF0],
            ],
            dtype=np.uint32,
        )
        guessed_key = np.array(
            [0x1B1A1918, 0x13121110, 0x0B0A0908, 0x03020100], dtype=np.uint32
        )
        round = 0
        mask = np.uint32(0xFF)

        hws = simon_64_128_simulation.get_hws_for_guessed_key_byte(
            plaintexts, guessed_key, round, mask
        )
        np.testing.assert_array_equal(hws, np.array([2, 0], dtype=np.uint32))
