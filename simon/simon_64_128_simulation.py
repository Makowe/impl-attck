import numpy as np

import logger


def log_to_simulated_power(log: logger.Log) -> np.ndarray:
    x_values = _get_x_values_from_log(log)
    return bits_count(x_values)


def get_hws_for_guessed_keys(
    plaintexts: np.ndarray, keys: np.ndarray, round: int, mask: np.uint32
) -> np.ndarray:
    """Perform the specified number of rounds on multiple plaintexts and multiple keys
    and return the hamming weight of the intermediate x state for each combination of plaintext and key.
    Example:
        plaintexts.shape = (10000, 2)   # 10,000 plaintexts each with 2 words
        keys.shape = (256, 4)           # 256 keys each with 4 words
        result.shape == (10000, 256)
    """
    if plaintexts.ndim == 1:
        plaintexts = plaintexts.reshape((1, 2))
    assert plaintexts.shape[1] == 2

    if keys.ndim == 1:
        keys = keys.reshape((1, 4))
    assert keys.shape[1] == 4

    xs = get_xs_after_round(plaintexts, keys, round)
    return bits_count(xs & mask).astype(np.uint32)


bits_count = np.frompyfunc(int.bit_count, 1, 1)


def get_xs_after_round(
    plaintexts: np.ndarray, keys: np.ndarray, round: int
) -> np.ndarray:
    """Perform the specified number of rounds on multiple plaintexts and multiple keys
    and return the intermediate x state for each combination of plaintext and key.
    Example:
        plaintexts.shape = (10000, 2)   # 10,000 plaintexts each with 2 words
        keys.shape = (256, 4)           # 256 keys each with 4 words
        result.shape == (10000, 256)
    """
    if plaintexts.ndim == 1:
        plaintexts = plaintexts.reshape((1, 2))
    assert plaintexts.shape[1] == 2

    if keys.ndim == 1:
        keys = keys.reshape((1, 4))
    assert keys.shape[1] == 4

    assert 0 <= round < 4

    round_keys = np.zeros_like(keys)
    round_keys[:, 0] = keys[:, 3]
    round_keys[:, 1] = keys[:, 2]
    round_keys[:, 2] = keys[:, 1]
    round_keys[:, 3] = keys[:, 0]

    x = np.repeat(plaintexts[:, 0:1], keys.shape[0], axis=1)
    y = np.repeat(plaintexts[:, 1:2], keys.shape[0], axis=1)

    # Perform the rounds.
    for i in range(round + 1):
        tmp = x.copy()
        x = (
            y
            ^ (((x << 1) | (x >> 31)) & ((x << 8) | (x >> 24)))
            ^ ((x << 2) | (x >> 30))
            ^ round_keys[:, i]
        )
        y = tmp

    return x


# PRIVATE


def _get_x_values_from_log(log: logger.Log) -> np.ndarray:
    x_values = []
    for e in log.entries:
        if e.label.startswith("X"):
            x_values.append(e.content[0])
    return np.array(x_values, dtype=np.uint32)
