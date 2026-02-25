from typing import Literal
import numpy as np

import simon_64_128_simulation
import correlations

from measurement import Measurements

bits_count = np.frompyfunc(int.bit_count, 1, 1)


class KeyHypothesis:
    """Wrapper for a guessed key and the correlation to the measurement.
    The argument `bit_mask` tells which bits in the Key are guessed.
    """

    def __init__(
        self,
        key: np.ndarray,
        bit_mask: np.ndarray,
        corr: np.float64 = np.float64(0.0),
    ):
        self.key = np.copy(key)
        self.bit_mask = np.copy(bit_mask)
        self.corr = corr

    def get_intermediate_mask(
        self, attacked_round: int, attacked_state: Literal["ADD_ROUND_KEY", "AND_GATE"]
    ) -> np.uint32:
        """Create a bitmask which has all bits set to 1 where the guessed key bits have influence on the attacked intermediate state.

        Example:
        ```
            When attacking the state after adding the round key, each guessed key bit has influence on exactly 1 bit of the intermediate state
            self.bit_mask = [0x00000000, 0x00000000, 0x00000000, 0x0000FFFF], attacked_round = 0, attacked_state = ADD_ROUND_KEY
            -> intermediate_mask = 0x0000FFFF

            self.bit_mask = [0x00000000, 0x00000000, 0x00FFFFFF, 0xFFFFFFFF], attacked_round = 1, attacked_state = ADD_ROUND_KEY
            -> intermediate_mask = 0x00FFFFFF

            When attacking the state after the AND gate, the resulting mask should only have the bits which can be predicted with the guessed key.
            self.bit_mask = [0x00000000, 0x00000000, 0x00000000, 0x0000FFFF], attacked_round = 0, attacked_state = AND_GATE
            -> intermediate_mask = 0x0001FF00
        ```
        """

        key_mask = self.bit_mask[3 - attacked_round]

        if attacked_state == "ADD_ROUND_KEY":
            intermediate_mask = key_mask
        elif attacked_state == "AND_GATE":
            # based on the key mask, perform the rotations (<<<1 and <<<8) to get all bits which can be predicted with the guessed key.
            intermediate_mask = np.uint32(
                ((key_mask << 1) | (key_mask >> 31))
                & ((key_mask << 8) | (key_mask >> 24))
            )
        else:
            raise ValueError(f"Invalid attacked state: {attacked_state}")
        return intermediate_mask

    def get_sub_hypos(self, new_mask: np.ndarray) -> list["KeyHypothesis"]:
        """Get a list of all sub hypothesis for the current hypothesis with additionally guessed bits according to the new mask

        Example:
        ```
        self = KeyHypothesis([0x00000000, 0x00000000, 0x00000000, 0x0000A4F3]
        new_mask = [0x00000000, 0x00000000, 0x00000000, 0x00FFFFFF]
        result =
        [ KeyHypothesis([0x00000000, 0x00000000, 0x00000000, 0x0000A4F3], 3)
          KeyHypothesis([0x00000000, 0x00000000, 0x00000000, 0x0001A4F3], 3)
          ...
          KeyHypothesis([0x00000000, 0x00000000, 0x00000000, 0x00FFA4F3], 3) ]
        ```
        """

        # Calculate number of bits which are newly guessed
        new_bits = new_mask & ~self.bit_mask
        num_new_bits = np.sum(bits_count(new_bits))

        # Array with new key guesses. The number of keys is based on the number of newly guessed bits.
        # If 8 additional bits are guessed, there will be 256 new keys with all combinations of the guessed bits.
        new_key_vals = np.tile(self.key, (2**num_new_bits, 1))

        helper_vals = np.arange(2**num_new_bits, dtype=np.uint32)

        new_bit_idx = 0
        for word_idx in range(3, -1, -1):
            for abs_bit_idx in range(32):
                # If the current bit is a newly guessed bit, set the values in new_key_vals according to the helper_vals.
                if new_bits[word_idx] & (1 << abs_bit_idx):
                    new_key_vals[:, word_idx] |= (
                        (helper_vals >> new_bit_idx) & 1
                    ) << abs_bit_idx
                    new_bit_idx += 1

        return [
            KeyHypothesis(new_key_vals[i], new_mask) for i in range(len(new_key_vals))
        ]


def filter_hypos(hypos: list[KeyHypothesis], threshold: float) -> list[KeyHypothesis]:
    """Go through a list of key hypotheses and creates a new list which only
    contains promising hypotheses.
    """

    best_corr = max([abs(h.corr) for h in hypos])
    remaining_hypotheses = [h for h in hypos if abs(h.corr) > best_corr - threshold]
    return remaining_hypotheses


def calc_corrs_for_hypos(
    hypos: list[KeyHypothesis],
    measurements: Measurements,
    attacked_round: int,
    attacked_state: Literal["ADD_ROUND_KEY", "AND_GATE"] = "ADD_ROUND_KEY",
):
    """For each combination of key and plaintext, calculate the hammmings weight of the attacked state.
    Calculate the correlation between the calculate hamming weights and power traces.
    For each hypothesis, find the maximum correlation over time.
    Write the result to the hypothesis object.
    """
    mask = hypos[0].get_intermediate_mask(attacked_round, attacked_state)

    keys = np.array([hypo.key for hypo in hypos], dtype=np.uint32)

    expected_hws = simon_64_128_simulation.get_hws_for_guessed_keys(
        measurements.plaintext, keys, attacked_round, mask, attacked_state
    )

    corrs = correlations.calc_corrs(expected_hws, measurements.power)
    for hypo, corr in zip(hypos, corrs):
        if np.max(corr) > -np.min(corr):
            hypo.corr = np.max(corr)
        else:
            hypo.corr = np.min(corr)


def array_to_hex_str(val: np.ndarray) -> str:
    if val.dtype == np.uint8:
        return " ".join(f"0x{e:02X}" for e in val)
    else:
        return " ".join(f"0x{e:08X}" for e in val)
