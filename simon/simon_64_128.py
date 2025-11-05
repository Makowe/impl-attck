import numpy as np


N = 32
M = 4
Z = np.uint64(0b0011011011101011000110010111100000010010001010011100110100001111)
T = 44


def encrypt_block(plaintext: np.ndarray, key: np.ndarray) -> np.ndarray:
    """Encrypt a single block using Simon."""
    assert plaintext.dtype == np.uint32
    assert key.dtype == np.uint32
    assert plaintext.shape == (2,)
    assert key.shape == (M,)

    # Prepare buffers
    round_keys = expand_key(key)
    x = plaintext[0]
    y = plaintext[1]

    # Perform the rounds.
    for i in range(T):
        tmp = x
        x = (
            y
            ^ (rotate_left(x, 1) & rotate_left(x, 8))
            ^ rotate_left(x, 2)
            ^ round_keys[i]
        )
        y = tmp

    return np.array([x, y], dtype=np.uint32)


def expand_key(key: np.ndarray) -> np.ndarray:

    # Result array will have m keys, each m*n bits long.
    k = np.zeros((T,), dtype=np.uint32)
    for i in range(M):
        k[i] = key[M - i - 1]

    for i in range(M, T):
        tmp = rotate_left(k[i - 1], -3) ^ k[i - 3]
        tmp ^= rotate_left(tmp, -1)

        z_i = get_round_constant(i - M)
        k[i] = ~k[i - M] ^ tmp ^ z_i ^ 3

    return k


def rotate_left(word: np.uint32, bits: int) -> np.uint32:
    """Rotate a word left."""
    if bits >= 0:
        return (word << bits | word >> (N - bits))
    else:
        bits = -bits
        return (word >> bits | word << (N - bits))


def get_round_constant(round: int) -> np.uint32:
    """Get the round constant for a given round."""
    return np.uint32((Z >> (61 - round)) & 1)
