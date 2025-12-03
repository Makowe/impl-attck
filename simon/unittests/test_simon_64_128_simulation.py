import unittest

import numpy as np

import simon_64_128_simulation


class TestSimon_64_128_Simulation(unittest.TestCase):
    def test_get_x_after_round(self):
        keys = np.array(
            [
                [0x1B1A1918, 0x13121110, 0x0B0A0908, 0x03020100],
                [0x00000000, 0x00000000, 0x00000000, 0x00000000],
            ],
            dtype=np.uint32,
        )
        plaintexts = np.array(
            [[0x656B696C, 0x20646E75], [0x00000000, 0x00000000]], dtype=np.uint32
        )

        x_after_round_0 = simon_64_128_simulation.get_xs_after_round(
            plaintexts, keys, 0
        )
        self.assertEqual(x_after_round_0.shape, (2, 2))
        self.assertEqual(x_after_round_0[0, 0], 0xFC8B8A84)

        x_after_round_3 = simon_64_128_simulation.get_xs_after_round(
            plaintexts, keys, 3
        )
        self.assertEqual(x_after_round_3.shape, (2, 2))
        self.assertEqual(x_after_round_3[0, 0], 0xE0C1D225)

    def test_get_hws_for_guessed_key_byte(self):
        keys = np.array(
            [
                [0x1B1A1918, 0x13121110, 0x0B0A0908, 0x03020100],
                [0x00000000, 0x00000000, 0x00000000, 0x00000000],
            ],
            dtype=np.uint32,
        )
        plaintexts = np.array(
            [[0x656B696C, 0x20646E75], [0x00000000, 0x00000000]], dtype=np.uint32
        )

        round = 0
        mask = np.uint32(0xFF)

        hws = simon_64_128_simulation.get_hws_for_guessed_keys(
            plaintexts, keys, round, mask
        )

        self.assertEqual(hws.shape, (2, 2))
        self.assertEqual(hws[0, 0], 2)
