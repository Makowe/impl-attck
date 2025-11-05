import numpy as np

import simon


algo = simon.SIMON_64_128
key = np.array(
    [0x1B1A1918, 0x13121110, 0x0B0A0908, 0x03020100], dtype=np.uint64
)

plaintext = np.array([0x656B696C, 0x20646E75], dtype=np.uint64)


print(f"Encrypting text {plaintext} with key {key}.")
ciphertext = simon.encrypt_block(algo, plaintext, key)


print(f"Encrypted text: {ciphertext}")