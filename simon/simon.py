import numpy as np


class Simon:
    def __init__(self, n: int, m: int, j: int, t: int):

        # Algorithm parameters.
        self.n = n
        """Number of bits in a word."""

        self.m = m
        """Number of words in the key."""

        self.j = j
        """Constant sequence for key schedule."""

        self.t = t
        """Number of rounds."""

        # Helper parameters derived from the actual algorithm parameters.
        self.block_size = 2 * n
        """Block size in bits."""

        self.bytes_in_word = n // 8
        """Number of bytes in a word."""

        self.key_size_bits = n * m
        """Key size in bits."""

        self.key_size_bytes = (n * m) // 8
        """Key size in bytes."""

        self.mask = ~np.uint64(0) >> (64 - n)
        """ Mask to apply on uint64 to keep only n bits."""


SIMON_32_64 = Simon(16, 4, 0, 32)
SIMON_48_72 = Simon(24, 3, 0, 36)
SIMON_48_96 = Simon(24, 4, 1, 36)
SIMON_64_96 = Simon(32, 3, 2, 42)
SIMON_64_128 = Simon(32, 4, 3, 44)
SIMON_96_96 = Simon(48, 2, 2, 52)
SIMON_96_144 = Simon(48, 3, 3, 54)
SIMON_128_128 = Simon(64, 2, 2, 68)
SIMON_128_192 = Simon(64, 3, 3, 69)
SIMON_128_256 = Simon(64, 4, 4, 72)


Z = np.array(
    [
        0b0011111010001001010110000111001101111101000100101011000011100110,
        0b0010001110111110010011000010110101000111011111001001100001011010,
        0b0010101111011100000011010010011000101000010001111110010110110011,
        0b0011011011101011000110010111100000010010001010011100110100001111,
        0b0011010001111001101011011000100000010111000011001010010011101111,
    ],
    dtype=np.uint64,
)
"""5 different sequences of round constants. Each sequence contains 62 1-bit constants.
Which sequence to use depends on parameter j of the Simon mode."""


def encrypt_block(algo: Simon, plaintext: np.ndarray, key: np.ndarray) -> np.ndarray:
    """Encrypt a single block using Simon."""
    assert plaintext.dtype == np.uint64
    assert key.dtype == np.uint64
    assert plaintext.shape == (2,)
    assert key.shape == (algo.m,)
    plaintext = clean_input(plaintext, algo)
    key = clean_input(key, algo)

    # Prepare buffers
    round_keys = expand_key(algo, key)
    x = plaintext[0]
    y = plaintext[1]

    # Perform the rounds.
    for i in range(algo.t):
        tmp = x
        x = (
            y
            ^ (rotate_left(x, 1, algo) & rotate_left(x, 8, algo))
            ^ rotate_left(x, 2, algo)
            ^ round_keys[i]
        )
        y = tmp

    return np.array([x, y], dtype=np.uint64)


def clean_input(input: np.ndarray, algo: Simon) -> np.ndarray:
    """Clean an array of words to ensure each only has n bits."""
    return input & algo.mask


def expand_key(algo: Simon, key: np.ndarray) -> np.ndarray:

    # Result array will have m keys, each m*n bits long.
    k = np.zeros((algo.t,), dtype=np.uint64)
    for i in range(algo.m):
        k[i] = key[algo.m - i - 1]

    for i in range(algo.m, algo.t):
        tmp = rotate_left(k[i - 1], -3, algo)
        if algo.m == 4:
            tmp ^= k[i - 3]
        tmp ^= rotate_left(tmp, -1, algo)

        z_i = get_round_constant(algo.j, i - algo.m)
        k[i] = invert(k[i - algo.m], algo) ^ tmp ^ z_i ^ 3

    return k


def expand_key_alt(algo: Simon, key: np.ndarray) -> np.ndarray:
    # Result array will have m keys, each m*n bits long.
    k = np.zeros((algo.t,), dtype=np.uint64)
    for i in range(algo.m):
        k[i] = key[algo.m - i - 1]

    # Constant c = 2^n - 4
    c = (~np.uint64(0) >> (64 - algo.n)) - 3

    for i in range(0, algo.t - algo.m):
        z_i = get_round_constant(algo.j, i)
        if algo.m == 2:
            tmp1 = rotate_left(k[i + 1], -3, algo)
            tmp2 = rotate_left(tmp1, -1, algo)
            k[i + algo.m] = c ^ z_i ^ k[i] ^ tmp1 ^ tmp2
        if algo.m == 3:
            tmp1 = rotate_left(k[i + 2], -3, algo)
            tmp2 = rotate_left(tmp1, -1, algo)
            k[i + algo.m] = c ^ z_i ^ k[i] ^ tmp1 ^ tmp2
        if algo.m == 4:
            tmp1 = rotate_left(k[i + 3], -3, algo) ^ k[i + 1]
            tmp2 = rotate_left(tmp1, -1, algo)
            k[i + algo.m] = c ^ z_i ^ k[i] ^ tmp1 ^ tmp2
    return k


def invert(word: np.uint64, algo: Simon) -> np.uint64:
    """Invert a word of n bits."""
    if algo.n == 64:
        return ~word
    return (~word) & algo.mask


def rotate_left(word: np.uint64, bits: int, algo: Simon) -> np.uint64:
    """Rotate a word left."""
    if bits >= 0:
        return (word << bits | word >> (algo.n - bits)) & algo.mask
    else:
        bits = -bits
        return (word >> bits | word << (algo.n - bits)) & algo.mask


def get_round_constant(j: int, round: int) -> np.uint64:
    """Get the round constant for a given round."""
    return (Z[j] >> ((61 - round) % 62)) & 1
