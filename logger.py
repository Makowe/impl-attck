import numpy as np

LOG_ST = []

def print_arr(st: np.ndarray):
    if st.ndim > 1:
        [print_arr(sub_st) for sub_st in st]
    else:
        print(" ".join(["{0:02X}".format(b) for b in st]))

def log_state(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        print_arr(res)
        LOG_ST.append(res)
        return res
    return wrapper
