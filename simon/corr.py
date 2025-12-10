import numpy as np


def calc_corrs(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Calculate the correlations between expected hamming weights and the power measurements
    at each time step.

    Example:
        x.shape = (10000, 256) # 10,000 measurements with 256 guessed keys each
        y.shape = (10000, 5000) # 10,000 measurements with 5,000 time steps each
        corrs(hws, power).shape -> (256, 5000) # for each of the 256 guessed keys, correlation values over 5,000 time steps.
    """
    assert x.shape[0] == y.shape[0]

    xc = x - x.mean()
    yc = y - y.mean(axis=0)

    xn = xc / xc.std(axis=0)
    yn = yc / yc.std(axis=0)

    corrs = xn.T @ yn / (x.shape[0] - 1)
    return corrs


class Corr:
    def __init__(self, shape: tuple):
        """Create a correlation calculator for data with the specified shape.
        Example:
            X represents hamming weights for 256 guessed keys
            Y represents power measurements for 5000 time steps
            -> shape = (256, 5000)
        """
        self.n = 0
        self.shape = shape
        self.mx = np.zeros(shape[0], dtype=np.float64)
        self.mxx = np.zeros(shape[0], dtype=np.float64)

        self.my = np.zeros(shape[1], dtype=np.float64)
        self.myy = np.zeros(shape[1], dtype=np.float64)

        self.mxy = np.zeros(shape, dtype=np.float64)

    def update(self, x_new: np.ndarray, y_new: np.ndarray):
        """ Add a bunch of measurements to the correlation calculation.
        Example:
            x_new.shape = (100, 256)
            y_new.shape = (100, 5000)
            This will increase n by 100 and update all intermediate values.
            The resulting correlations will have shape (256, 5000).
        """
        assert x_new.shape[0] == y_new.shape[0]
        assert x_new.shape[1] == self.shape[0]
        assert y_new.shape[1] == self.shape[1]

        self.n += x_new.shape[0]

        dx = x_new - self.mx
        dy = y_new - self.mx

        self.mx += dx.sum(axis=0) / self.n
        self.my += dy.sum(axis=0) / self.n

        dx2 = x_new - self.mx
        dy2 = y_new - self.my

        self.mxx += np.sum(dx * dx2, axis=0)
        self.myy += np.sum(dy * dy2, axis=0)
        self.mxy += dx.T @ dy2


    def c(self) -> np.ndarray:
        num = self.mxy
        den = (self.mxx.reshape((self.shape[0], 1)) @ self.myy.reshape((1, self.shape[1]))) ** 0.5
        return num / den
    