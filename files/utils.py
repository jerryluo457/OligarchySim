# utils.py
import numpy as np

def gaussian_noise(d, scale):
    return np.random.normal(0, scale, size=d)
