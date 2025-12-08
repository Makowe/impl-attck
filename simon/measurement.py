import numpy as np


class Measurement:
    def __init__(
        self,
        plaintext: np.ndarray,
        ciphertext: np.ndarray,
        power: np.ndarray,
    ):
        self.plaintext = plaintext
        self.ciphertext = ciphertext
        self.power = power


class Measurements:
    def __init__(
        self, plaintext: np.ndarray, ciphertext: np.ndarray, power: np.ndarray
    ):
        self.plaintext = plaintext
        self.ciphertext = ciphertext
        self.power = power

    def __getitem__(self, i) -> "Measurements | Measurement":
        if isinstance(i, slice):
            return Measurement(
                self.plaintext[i],
                self.ciphertext[i],
                self.power[i],
            )

        return Measurement(self.plaintext[i], self.ciphertext[i], self.power[i])
