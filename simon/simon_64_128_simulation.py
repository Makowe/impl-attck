import numpy as np

import logger
import simon_64_128


def log_to_simulated_power(log: logger.Log) -> np.ndarray:
    x_values = _get_x_values_from_log(log)
    return np.bitwise_count(x_values)


def get_hws_for_guessed_key_byte(
    plaintexts: np.ndarray, guessed_key: np.ndarray, round: int, mask: np.uint32
) -> int:
    
    xs = np.apply_along_axis(
        get_x_after_round, 1, plaintexts, guessed_key, round
    )
    return bits_count(xs & mask).astype(np.uint32)


bits_count = np.frompyfunc(int.bit_count, 1, 1)

def get_x_after_round(plaintext: np.ndarray, key: np.ndarray, round: int) -> np.ndarray:
    """Perform only the first 4 rounds of the encryption.
    This is useful for side-channel simulations where only the states of the first 4 rounds are required.
    Instead of the ciphertext, return the four states x[1..4] for analysis.
    """
    assert plaintext.dtype == np.uint32
    assert key.dtype == np.uint32
    assert plaintext.shape == (2,)
    assert key.shape == (simon_64_128.M,)

    # Prepare buffers
    round_keys = np.array([key[3], key[2], key[1], key[0]], dtype=np.uint32)

    x = plaintext[0:1]
    y = plaintext[1:2]

    # Perform the rounds.
    for i in range(round+1):
        tmp = x
        x = (
            y
            ^ (simon_64_128.rotate_left(x, 1) & simon_64_128.rotate_left(x, 8))
            ^ simon_64_128.rotate_left(x, 2)
            ^ round_keys[i:i+1]
        )
        y = tmp

    return x[0]


# PRIVATE


def _get_x_values_from_log(log: logger.Log) -> np.ndarray:
    x_values = []
    for e in log.entries:
        if e.label.startswith("X"):
            x_values.append(e.content)
    return np.array(x_values, dtype=np.uint32)
