import numpy as np
import aes128
import logger


# plaintext =np.array([0x32, 0x43, 0xf6, 0xa8, 0x88, 0x5a, 0x30, 0x8d, 0x31, 0x31, 0x98, 0xa2, 0xe0, 0x37, 0x07, 0x34], dtype=np.uint8)
# key =np.array([0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6, 0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c], dtype=np.uint8)

plaintext1 = np.zeros(16, dtype=np.uint8)
plaintext2 = np.zeros(16, dtype=np.uint8)
plaintext2[0] = 1

key1 = np.zeros(16, dtype=np.uint8)
key2 = np.zeros(16, dtype=np.uint8)
key2[0] = 1


expanded_key1 = aes128.expand_key(key1)
print("Expanded Key 1:")
logger.print_arr(expanded_key1)

expanded_key2 = aes128.expand_key(key2)
print("Expanded Key 2:")
logger.print_arr(expanded_key2)

key_diff = expanded_key1 ^ expanded_key2
print("Key Diff:")
logger.print_arr(key_diff)

print("Cipher1")
res = aes128.encrypt_block(plaintext1, key1)
log1 = logger.LOG_ST
logger.LOG_ST = []

print("Cipher2")
res = aes128.encrypt_block(plaintext1, key2)
log2 = logger.LOG_ST
logger.LOG_ST = []

# Compare
log1 = np.array(log1)
log2 = np.array(log2)

cipher_diff = log1 ^ log2

print("Diff")
logger.print_arr(cipher_diff)
