# dynamics.py
import numpy as np

class Dynamics:
    def __init__(self, policy, publicPreference, theta):
        self.policy = np.array(policy)
        self.publicPreference = np.array(publicPreference)
        self.theta = theta
    
    def updatePolicy(self, eliteInterest, publicInterest, theta):
        eliteInterest = np.array(eliteInterest)
        publicInterest = np.array(publicInterest)
        self.policy = theta * publicInterest + (1 - theta) * eliteInterest
        return self.policy
    
    def updatePublicPreference(self, originalPublicPref, policyOutcome, eta, noise):
        originalPublicPref = np.array(originalPublicPref)
        policyOutcome = np.array(policyOutcome)
        noise = np.array(noise)
        self.publicPreference = originalPublicPref + eta * (policyOutcome - originalPublicPref) + noise
        return self.publicPreference
    
    def updateTheta(self, eci, lambd, alpha, theta_star):
        """
        New Math: theta(t+1) = theta(t) + alpha * (theta* - theta(t)) - lambda * ECI(t)
        """
        recovery = alpha * (theta_star - self.theta)
        erosion = lambd * eci
        self.theta = self.theta + recovery - erosion
        self.theta = np.clip(self.theta, 0.0, 1.0)
        return self.theta