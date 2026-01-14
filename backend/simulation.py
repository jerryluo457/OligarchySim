# simulation.py
import numpy as np

from elites import Elites
from dynamics import Dynamics
from metrics import eliteCaptureIndex
from state import State
import config
from utils import gaussian_noise


def run_simulation():
    # initialize elites
    elites = Elites(config.eliteInfoDict)

    # initialize dynamics
    dynamics = Dynamics(
        policy=config.M_0,
        publicPreference=config.M_0,
        theta=config.theta_0
    )

    # initial state
    states = []

    M = config.M_0
    theta = config.theta_0

    for t in range(config.T):
        # compute elite centroid
        E = elites.computeEliteCentroid()

        # update policy
        O = dynamics.updatePolicy(
            eliteInterest=E,
            publicInterest=M,
            theta=theta
        )

        # compute elite capture
        eci = eliteCaptureIndex(M, E, O)

        # update public preference
        noise = gaussian_noise(config.d, config.noise_scale)
        M = dynamics.updatePublicPreference(
            originalPublicPref=M,
            policyOutcome=O,
            eta=config.eta,
            noise=noise
        )

        # update elite weights
        elites.updateWeights(
            weights=elites.eliteInfluenceList,
            elitePoints=elites.elitePrefenceList,
            outcome=O,
            kappa=config.kappa
        )

        # update responsiveness
        theta = dynamics.updateTheta(eci, config.lambd)

        # store state snapshot
        state = State(
            M=M,
            E=E,
            O=O,
            w=elites.eliteInfluenceList,
            theta=theta,
            t=t
        )
        states.append(state)

    return states


if __name__ == "__main__":
    states = run_simulation()
    print("Simulation complete.")
    print("Final policy outcome:", states[-1].getPolicyOutcome())
    print("Final responsiveness:", states[-1].getDemResponsv())
    print("Final ECI:", eliteCaptureIndex(states[-1].getMedVoterPref(), states[-1].getEliteCentroid(), states[-1].getPolicyOutcome()))
