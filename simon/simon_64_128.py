import numpy as np
import logger


N = 32
M = 4
Z = np.array(
    [0b0011011011101011000110010111100000010010001010011100110100001111],
    dtype=np.uint64,
)
T = 44


def encrypt_block(
    plaintext: np.ndarray, key: np.ndarray
) -> tuple[np.ndarray, logger.Log]:
    """Encrypt a single block using Simon.
    Return the ciphertext and a log of the intermediate values.
    """
    assert plaintext.dtype == np.uint32
    assert key.dtype == np.uint32
    assert plaintext.shape == (2,)
    assert key.shape == (M,)

    log = logger.Log()

    log.add(plaintext, "Plaintext")
    log.add(key, "Key")

    # Prepare buffers
    round_keys = expand_key(key)
    log.add(round_keys, "Expanded Key")

    # Initialize state. Use an array of size 1 for each word.
    # Required for compatibility with numpy.
    x = plaintext[0:1]
    y = plaintext[1:2]

    log.add(x, f"X0")
    log.add(y, f"Y0")

    # Perform the rounds.
    for i in range(T):
        log.add(f"=== Perform Round {i+1} ===")
        tmp = x
        x = (
            y
            ^ (rotate_left(x, 1) & rotate_left(x, 8))
            ^ rotate_left(x, 2)
            ^ round_keys[i : i + 1]
        )
        y = tmp
        log.add(x, f"X{i+1}")
        log.add(y, f"Y{i+1}")

    res = np.array([x[0], y[0]], dtype=np.uint32)
    return res, log


def expand_key(key: np.ndarray) -> np.ndarray:

    # Result array will have m keys, each m*n bits long.
    expanded_key = np.zeros((T,), dtype=np.uint32)
    expanded_key[0] = key[3]
    expanded_key[1] = key[2]
    expanded_key[2] = key[1]
    expanded_key[3] = key[0]

    for i in range(M, T):

        tmp = rotate_left(expanded_key[i - 1 : i], -3) ^ expanded_key[i - 3 : i - 2]
        tmp ^= rotate_left(tmp, -1)

        z_i = get_round_constant(i - M)
        expanded_key[i] = (~expanded_key[i - M] ^ tmp ^ z_i ^ 3)[0]

    return expanded_key


def rotate_left(word: np.ndarray, bits: int) -> np.ndarray:
    """Rotate a word left."""
    if bits >= 0:
        return word << bits | word >> (N - bits)
    else:
        bits = -bits
        return word >> bits | word << (N - bits)


def get_round_constant(round: int) -> np.ndarray:
    """Get the round constant for a given round."""
    return (Z >> (61 - round)) & 1
