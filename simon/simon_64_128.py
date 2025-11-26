import numpy as np
import logger


N = 32
M = 4
Z = np.uint64(0b0011011011101011000110010111100000010010001010011100110100001111)
T = 44


def encrypt_block(
    plaintext: np.ndarray, key: np.ndarray
) -> tuple[np.ndarray, logger.Log]:
    """Encrypt a single block using Simon."""
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

    x = plaintext[0]
    y = plaintext[1]

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
            ^ round_keys[i]
        )
        y = tmp
        log.add(x, f"X{i+1}")
        log.add(y, f"Y{i+1}")

    res = np.array([x, y], dtype=np.uint32)
    return res, log


def expand_key(key: np.ndarray) -> np.ndarray:

    # Result array will have m keys, each m*n bits long.
    res = np.zeros((T,), dtype=np.uint32)
    res[0] = key[3]
    res[1] = key[2]
    res[2] = key[1]
    res[3] = key[0]

    for i in range(M, T):
        tmp = rotate_left(res[i - 1], -3) ^ res[i - 3]
        tmp ^= rotate_left(tmp, -1)

        z_i = get_round_constant(i - M)
        res[i] = ~res[i - M] ^ tmp ^ z_i ^ 3

    return res


def rotate_left(word: np.uint32, bits: int) -> np.uint32:
    """Rotate a word left."""
    if bits >= 0:
        return word << bits | word >> (N - bits)
    else:
        bits = -bits
        return word >> bits | word << (N - bits)


def get_round_constant(round: int) -> np.uint32:
    """Get the round constant for a given round."""
    return np.uint32((Z >> (61 - round)) & 1)
