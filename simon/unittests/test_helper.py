import unittest
import numpy as np
import helper


class TestHelper(unittest.TestCase):
    def test_key_hypothesis(self):
        h1 = helper.KeyHypothesis(
            np.array([0x00000000, 0x00000000, 0x00000000, 0x00001234], dtype=np.uint32),
            2,
        )
        h2 = helper.KeyHypothesis(
            np.array([0x00000000, 0x00000000, 0x00000000, 0x12345678], dtype=np.uint32),
            4,
        )
        h3 = helper.KeyHypothesis(
            np.array([0x00000000, 0x00000000, 0x12345678, 0x12345678], dtype=np.uint32),
            8,
        )
        h4 = helper.KeyHypothesis(
            np.array([0x12345678, 0x12345678, 0x12345678, 0x12345678], dtype=np.uint32),
            16,
        )

        self.assertEqual(h1.get_round_to_attack(), 0)
        self.assertEqual(h2.get_round_to_attack(), 0)
        self.assertEqual(h3.get_round_to_attack(), 1)
        self.assertEqual(h4.get_round_to_attack(), 3)

    def test_key_hypothesis_iter(self):
        h1 = helper.KeyHypothesis(
            np.array([0x00000000, 0x00000000, 0x00000000, 0x00001234], dtype=np.uint32),
            2,
        )
        h3 = helper.KeyHypothesis(
            np.array([0x00000000, 0x00000000, 0x12345678, 0x12345678], dtype=np.uint32),
            8,
        )

        sub_hypos: list[helper.KeyHypothesis] = []
        for sub_hypo in h1.get_sub_hypos():
            sub_hypos.append(sub_hypo)
            self.assertEqual(sub_hypo.num_guessed_bytes, 3)
            self.assertEqual(sub_hypo.get_round_to_attack(), 0)

        self.assertEqual(len(sub_hypos), 256)
        np.testing.assert_array_equal(
            sub_hypos[0].key, np.array([0, 0, 0, 0x00001234], dtype=np.uint32)
        )
        np.testing.assert_array_equal(
            sub_hypos[5].key, np.array([0, 0, 0, 0x00051234], dtype=np.uint32)
        )
        np.testing.assert_array_equal(
            sub_hypos[255].key, np.array([0, 0, 0, 0x00FF1234], dtype=np.uint32)
        )

        sub_hypos: list[helper.KeyHypothesis] = []
        for sub_hypo in h3.get_sub_hypos():
            sub_hypos.append(sub_hypo)

        self.assertEqual(len(sub_hypos), 256)
        np.testing.assert_array_equal(
            sub_hypos[0].key,
            np.array([0x00000000, 0x00000000, 0x12345678, 0x12345678], dtype=np.uint32),
        )
        np.testing.assert_array_equal(
            sub_hypos[5].key,
            np.array([0x00000000, 0x00000005, 0x12345678, 0x12345678], dtype=np.uint32),
        )
        np.testing.assert_array_equal(
            sub_hypos[255].key,
            np.array([0x00000000, 0x000000FF, 0x12345678, 0x12345678], dtype=np.uint32),
        )

    def test_filter_hypos(self):
        h1 = helper.KeyHypothesis(
            np.array([0, 0, 0, 0], dtype=np.uint32), 2, np.float64(0.3)
        )
        h2 = helper.KeyHypothesis(
            np.array([0, 0, 0, 0], dtype=np.uint32), 2, np.float64(-0.3)
        )
        h3 = helper.KeyHypothesis(
            np.array([0, 0, 0, 0], dtype=np.uint32), 2, np.float64(0.5)
        )
        h4 = helper.KeyHypothesis(
            np.array([0, 0, 0, 0], dtype=np.uint32), 2, np.float64(-0.5)
        )
        h5 = helper.KeyHypothesis(
            np.array([0, 0, 0, 0], dtype=np.uint32), 2, np.float64(0.0)
        )

        self.assertEqual(helper.filter_hypos([h1], threshold=np.float64(0.1)), [h1])
        self.assertEqual(helper.filter_hypos([h2], threshold=np.float64(0.1)), [h2])
        self.assertEqual(
            helper.filter_hypos([h1, h2], threshold=np.float64(0.1)), [h1, h2]
        )
        self.assertEqual(helper.filter_hypos([h1, h3], threshold=np.float64(0.1)), [h3])
        self.assertEqual(
            helper.filter_hypos([h1, h3], threshold=np.float64(0.3)), [h1, h3]
        )
        self.assertEqual(
            helper.filter_hypos([h1, h3, h4], threshold=np.float64(0.1)), [h3, h4]
        )
        self.assertEqual(
            helper.filter_hypos([h1, h5], threshold=np.float64(0.4)), [h1, h5]
        )
