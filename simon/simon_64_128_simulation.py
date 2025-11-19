import numpy as np

import logger
import simon_64_128


def log_to_simulated_power(log: logger.Log) -> np.ndarray:
    x_values = _get_x_values_from_log(log)
    return np.bitwise_count(x_values)


def get_hw_for_guessed_key_byte(
    plaintext: np.ndarray, guessed_key: np.ndarray, round: int, mask: np.uint32
) -> int:
    x_i = _get_x_for_guessed_key(plaintext, guessed_key, round)
    return (x_i & mask).bit_count()


def encrypt_block_light(plaintext: np.ndarray, key: np.ndarray) -> np.ndarray:
    """Perform only the first 4 rounds of the encryption.
    This is useful for side-channel simulations where only the states of the first 4 rounds are required.
    Instead of the ciphertext, return the four states x[1..4] for analysis.
    """
    assert plaintext.dtype == np.uint32
    assert key.dtype == np.uint32
    assert plaintext.shape == (2,)
    assert key.shape == (simon_64_128.M,)

    res = np.array([0, 0, 0, 0], dtype=np.uint32)

    # Prepare buffers
    round_keys = np.array([key[3], key[2], key[1], key[0]], dtype=np.uint32)

    x = plaintext[0]
    y = plaintext[1]

    # Perform the rounds.
    for i in range(simon_64_128.M):
        tmp = x
        x = (
            y
            ^ (simon_64_128.rotate_left(x, 1) & simon_64_128.rotate_left(x, 8))
            ^ simon_64_128.rotate_left(x, 2)
            ^ round_keys[i]
        )
        y = tmp
        res[i] = x

    return res


# PRIVATE


def _get_x_values_from_log(log: logger.Log) -> np.ndarray:
    x_values = []
    for e in log.entries:
        if e.label.startswith("X"):
            x_values.append(e.content)
    return np.array(x_values, dtype=np.uint32)


def _get_x_for_guessed_key(
    plaintext: np.ndarray, guessed_key: np.ndarray, round: int
) -> np.integer:
    x_values = encrypt_block_light(plaintext, guessed_key)
    return x_values[round]
