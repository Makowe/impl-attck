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
    def __init__(self):
        self.entries: list["Measurement"] = []
        self.power_2d = np.array([], dtype=np.uint32)

    def __getitem__(self, i) -> "Measurement":
        return self.entries[i]

    def append(self, entry: "Measurement"):
        self.entries.append(entry)

    def update_power_2d(self):
        self.power_2d = np.array([m.power for m in self.entries], dtype=np.uint32)
