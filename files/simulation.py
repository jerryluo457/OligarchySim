# simulation.py
import numpy as np

from elites import Elites
from dynamics import Dynamics
from metrics import eliteCaptureIndex
from state import State
from utils import gaussian_noise

def run_simulation(T, M_0, theta_0, elite_data, eta, kappa, lambd, noise_scale, alpha, theta_star):
    # initialize elites
    elites = Elites(elite_data)

    # initialize dynamics
    dynamics = Dynamics(
        policy=M_0,
        publicPreference=M_0,
        theta=theta_0
    )

    states = []
    
    # State tracking
    M = np.array(M_0)
    theta = theta_0
    
    d = len(M_0)

    for t in range(T):
        # 1. Compute Elite Centroid
        # Uses the Elites class method which uses internal self.weights
        E = elites.computeEliteCentroid()

        # 2. Update Policy
        O = dynamics.updatePolicy(
            eliteInterest=E,
            publicInterest=M,
            theta=theta
        )

        # 3. Compute Metrics
        eci = eliteCaptureIndex(M, E, O)

        # 4. Update Public Preference
        noise = gaussian_noise(d, noise_scale)
        M = dynamics.updatePublicPreference(
            originalPublicPref=M,
            policyOutcome=O,
            eta=eta,
            noise=noise
        )

        # 5. Update Elite Weights
        # CRITICAL FIX: accessing .weights and .positions instead of .eliteInfluenceList
        elites.updateWeights(
            weights=elites.weights,
            elitePoints=elites.positions,
            outcome=O,
            kappa=kappa
        )

        # 6. Update Responsiveness (Using new params: alpha, theta_star)
        theta = dynamics.updateTheta(eci, lambd, alpha, theta_star)

        # 7. Store State
        state = State(
            M=M,
            E=E,
            O=O,
            w=elites.weights,
            theta=theta,
            t=t
        )
        states.append(state)

    return states