import numpy as np

import simon_64_128

key = np.array([0x1B1A1918, 0x13121110, 0x0B0A0908, 0x03020100], dtype=np.uint32)
plaintext1 = np.array([0x656B696C, 0x20646E75], dtype=np.uint32)
plaintext2 = np.array([0x656B696C, 0x20646E74], dtype=np.uint32)

ciphertext1, log1 = simon_64_128.encrypt_block(plaintext1, key)
ciphertext2, log2 = simon_64_128.encrypt_block(plaintext2, key)


print(log1.to_str())

print("\nLog 2\n")

print(log2.to_str())

print("\n XOR between Log 1 and Log 2\n")
print(log1.xor(log2).to_str(num_format="b"))
