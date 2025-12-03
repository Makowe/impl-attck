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
        self.plaintexts = np.array([], dtype=np.uint32)
        self.ciphertexts = np.array([], dtype=np.uint32)
        self.power_2d = np.array([], dtype=np.uint32)

    def __getitem__(self, i) -> "Measurement":
        return self.entries[i]

    def append(self, entry: "Measurement"):
        self.entries.append(entry)

    def update_arrays(self):
        self.power_2d = np.array([m.power for m in self.entries], dtype=np.uint32)
        self.plaintexts = np.array([m.plaintext for m in self.entries], dtype=np.uint32)
        self.ciphertexts = np.array([m.ciphertext for m in self.entries], dtype=np.uint32)
