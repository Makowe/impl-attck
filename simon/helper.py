import numpy as np

import simon_64_128_simulation

from measurement import Measurements, Measurement


class KeyHypothesis:
    """Wrapper for a guessed key and the correlation to the measurement.
    The argument `attack_step` tells in which attack round the Hypothesis was made.
    This is required for deriving sub-keys.
    """

    def __init__(
        self,
        key: np.ndarray,
        num_guessed_bytes: int,
        corr: np.float64 = np.float64(0.0),
    ):
        self.key = key
        self.num_guessed_bytes = num_guessed_bytes
        self.corr = corr

    def get_mask(self) -> np.uint32:
        return ~np.uint32(0) >> 32 - (self.num_guessed_bytes * 8)

    def get_sub_hypo(self, byte_val: int) -> "KeyHypothesis":
        byte_to_guess = self.num_guessed_bytes
        array_idx = 3 - (byte_to_guess // 4)
        array_offset = (byte_to_guess % 4) * 8
        new_key = self.key.copy()
        new_key[array_idx] &= ~np.uint32(0xFF << array_offset)
        new_key[array_idx] |= np.uint32(byte_val << array_offset)
        return KeyHypothesis(new_key, self.num_guessed_bytes + 1)

    def get_sub_hypos(self) -> list["KeyHypothesis"]:
        return [self.get_sub_hypo(byte_val) for byte_val in range(256)]

    def get_round_to_attack(self) -> int:
        return (self.num_guessed_bytes - 1) // 4


def filter_hypos(
    hypos: list[KeyHypothesis], threshold: np.float64
) -> list[KeyHypothesis]:
    """Goes through a list of key hypotheses and creates a new list where all declined
    hypotheses are removed.
    """

    best_corr = max([abs(h.corr) for h in hypos])
    remaining_hypotheses = [h for h in hypos if abs(h.corr) > best_corr - threshold]
    return remaining_hypotheses


def get_corr_for_hypo(hypo: KeyHypothesis, measurements: Measurements) -> np.float64:
    round_to_attack = hypo.get_round_to_attack()
    mask = hypo.get_mask()

    for m in measurements.entries:
        simon_64_128_simulation.get_hw_for_guessed_key_byte(
            m.plaintext, hypo.key, round_to_attack, mask
        )
    # TODO: finish this


def find_best_correlation(
    expected_hws: np.ndarray, consumptions: np.ndarray
) -> np.float64:
    # TODO: Fix this

    """Go through all timepoints and find the one with the maximum correlation to hamming weights (positive or negative).
    Example:
        - 1000 measurements, each with 45 timepoints
        - expected_hws: [8, ..., 1] # Shape = 1000
        - consumptions: [[27, ...,  17],
                         [30, ...,   2],
                         ...
                         [11, ...,  11]] # Shape = (1000, 45)
                           |    |    |
                          0.5  ...  0.1  <- Correlations for each timepoint
        - returns 0.5

    """
    assert expected_hws.shape[0] == consumptions.shape[0]

    correlations = np.array(
        [
            np.corrcoef(expected_hws, consumptions[:, t])[0, 1]
            for t in range(consumptions.shape[1])
        ],
        dtype=np.float64,
    )
    if np.max(correlations) > -np.min(correlations):
        return np.max(correlations)
    else:
        return np.min(correlations)


def array_to_hex_str(val: np.ndarray) -> str:
    if val.dtype == np.uint8:
        return " ".join(f"0x{e:02X}" for e in val)
    else:
        return " ".join(f"0x{e:08X}" for e in val)
