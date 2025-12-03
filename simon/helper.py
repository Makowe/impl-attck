import numpy as np

import simon_64_128_simulation

from measurement import Measurements, Measurement


class KeyHypothesis:
    """Wrapper for a guessed key and the correlation to the measurement.
    The argument `num_guessed_bytes` tells how many bytes in the Hypothesis are guessed.
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
        """Create a bitmask for the current round key where all guessed bits are set to 1.

        Example:
        ```
            KeyHypothesis([0x00000000, 0x00000000, 0x00000000, 0x0000A4F3], 2).get_mask() -> 0x0000FFFF
            KeyHypothesis([0x00000000, 0x00000000, 0x00000000, 0x263AD743], 4).get_mask() -> 0xFFFFFFFF
            KeyHypothesis([0x00000000, 0x00000000, 0x00343DF4, 0x3456DE76], 7).get_mask() -> 0x00FFFFFF
        ```
        """
        if self.num_guessed_bytes % 4 == 0:
            guessed_bytes_in_word = 4
        else:
            guessed_bytes_in_word = self.num_guessed_bytes % 4
        return ~np.uint32(0) >> 32 - (guessed_bytes_in_word * 8)

    def get_sub_hypo(self, byte_val: int) -> "KeyHypothesis":
        """Get a sub hypothesis for the current hypothesis with 1 additionally guessed byte

        Example:
        ```
        KeyHypothesis([0x00000000, 0x00000000, 0x00000000, 0x0000A4F3], 2).get_sub_hypo(0x27) ->
        KeyHypothesis([0x00000000, 0x00000000, 0x00000000, 0x0027A4F3], 3)
        ```
        """
        byte_to_guess = self.num_guessed_bytes
        array_idx = 3 - (byte_to_guess // 4)
        array_offset = (byte_to_guess % 4) * 8
        new_key = self.key.copy()
        new_key[array_idx] &= ~np.uint32(0xFF << array_offset)
        new_key[array_idx] |= np.uint32(byte_val << array_offset)
        return KeyHypothesis(new_key, self.num_guessed_bytes + 1)

    def get_sub_hypos(self) -> list["KeyHypothesis"]:
        """Get a list of all 256 sub hypothesis for the current hypothesis with 1 additionally guessed byte

        Example:
        ```
        KeyHypothesis([0x00000000, 0x00000000, 0x00000000, 0x0000A4F3], 2).get_sub_hypos() ->
        [ KeyHypothesis([0x00000000, 0x00000000, 0x00000000, 0x0000A4F3], 3)
          KeyHypothesis([0x00000000, 0x00000000, 0x00000000, 0x0001A4F3], 3)
          ...
          KeyHypothesis([0x00000000, 0x00000000, 0x00000000, 0x00FFA4F3], 3) ]
        ```
        """

        return [self.get_sub_hypo(byte_val) for byte_val in range(256)]

    def get_round_to_attack(self) -> int:
        """Create a bitmask for the current round key where all guessed bits are set to 1.
        Example:
            KeyHypothesis([0x00000000, 0x00000000, 0x00000000, 0x0000A4F3], 2).get_round_to_attack() -> 0
            KeyHypothesis([0x00000000, 0x00000000, 0x00000000, 0x263AD743], 4).get_round_to_attack() -> 0
            KeyHypothesis([0x00000000, 0x00000000, 0x00343DF4, 0x3456DE76], 7).get_round_to_attack() -> 1
        """
        return (self.num_guessed_bytes - 1) // 4


def filter_hypos(hypos: list[KeyHypothesis], threshold: float) -> list[KeyHypothesis]:
    """Goes through a list of key hypotheses and creates a new list where all declined
    hypotheses are removed.
    """

    best_corr = max([abs(h.corr) for h in hypos])
    remaining_hypotheses = [h for h in hypos if abs(h.corr) > best_corr - threshold]
    return remaining_hypotheses


def calc_corr_for_hypo(hypo: KeyHypothesis, measurements: Measurements):
    round_to_attack = hypo.get_round_to_attack()
    mask = hypo.get_mask()

    expected_hws = simon_64_128_simulation.get_hws_for_guessed_key_byte(
        measurements.plaintexts, hypo.key, round_to_attack, mask
    )

    corrs = calc_corrs(expected_hws, measurements.power_2d)
    if np.max(corrs) > -np.min(corrs):
        hypo.corr = np.max(corrs)
    else:
        hypo.corr = np.min(corrs)

def array_to_hex_str(val: np.ndarray) -> str:
    if val.dtype == np.uint8:
        return " ".join(f"0x{e:02X}" for e in val)
    else:
        return " ".join(f"0x{e:08X}" for e in val)


def calc_corrs(hws: np.ndarray, power: np.ndarray) -> np.ndarray:
    """Calculate the correlations between expected hamming weights and the power measurements
    at each time step.

    Example:
        hws.shape = (50000,) # 50,000 measurements
        power.shape = (50000, 1000) # 50,000 measurements with 1,000 time steps each
        corrs(hws, power).shape -> (1000,) # 1,000 correlation values, one for each time step
    """

    hws_c = hws - hws.mean()
    power_c = power - power.mean(axis=0)
    num = hws_c @ power_c
    den = np.sqrt((hws_c @ hws_c) * (power_c * power_c).sum(axis=0))
    corr = num / den
    return corr