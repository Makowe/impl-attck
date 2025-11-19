import numpy as np

class KeyHypothesis():
    def __init__(self, key: np.ndarray, corr: np.float64, attack_step: int):
        self.key = key
        self.corr = corr
        self.attack_step = attack_step


def filter_hypotheses(hypotheses: list[KeyHypothesis], threshold: np.float64) -> list[KeyHypothesis]:
    best_corr = max([abs(h.corr) for h in hypotheses])
    remaining_hypotheses = [h for h in hypotheses if abs(h.corr) > best_corr-threshold]
    return remaining_hypotheses
