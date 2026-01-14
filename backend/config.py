# config.py

import numpy as np

# simulation parameters
T = 100                     # number of political cycles
d = 2                       # policy dimension
K = 5                       # number of elites

# learning / evolution parameters
eta = 0.1                   # public learning rate
kappa = 1.0                 # elite influence sensitivity
lambd = 0.01                # responsiveness decay

# initial conditions
theta_0 = 0.7
M_0 = np.zeros(d)
noise_scale = 0.01

# elite setup: {elite_point: initial_weight}
eliteInfoDict = {
    (-1.0, -1.0): 0.2,
    (-0.5, -0.5): 0.2,
    ( 0.0,  0.0): 0.2,
    ( 0.5,  0.5): 0.2,
    ( 1.0,  1.0): 0.2
}
