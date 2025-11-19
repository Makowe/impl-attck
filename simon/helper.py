import numpy as np


class KeyHypothesisIterator:
    """Iterator to generate new key hypotheses from an existing base key.
    Example:

    - `Base Key`:
    ```
    0x00000000 0x00000000 0x00000000 0x00003DA5
    ```
    - `new_byte_idx = 3`
    - `new_byte_offset = 16`

    In the base key, 2 bytes are guessed already.
    Now generate new keys where the third byte is guessed.

    New Key Guesses:
    ```
    0x00000000 0x00000000 0x00000000 0x00003DA5
    0x00000000 0x00000000 0x00000000 0x00013DA5
    ...
    0x00000000 0x00000000 0x00000000 0x00FF3DA5
    ```
    """

    def __init__(self, base_hypothesis: "KeyHypothesis") -> None:
        self.base_key = base_hypothesis.key
        self.byte_to_guess = base_hypothesis.num_guessed_bytes

        self.array_idx = 3 - (self.byte_to_guess // 4)
        self.array_offset = (self.byte_to_guess % 4) * 8

        self.next_byte_val: int = 0

    def __iter__(self):
        return self

    def __next__(self) -> "KeyHypothesis":
        if self.next_byte_val > 0xFF:
            raise StopIteration

        new_key = self.base_key.copy()
        new_key[self.array_idx] &= ~np.uint32(0xFF << self.array_offset)
        new_key[self.array_idx] |= np.uint32(self.next_byte_val << self.array_offset)
        self.next_byte_val += 1
        return KeyHypothesis(new_key, self.byte_to_guess + 1)


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

    def get_sub_hypos(self) -> KeyHypothesisIterator:
        return KeyHypothesisIterator(self)

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
