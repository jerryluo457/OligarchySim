# dynamics.py
import numpy as np

class Dynamics:
    def __init__(self, policy, publicPreference, theta):
        self.policy = np.array(policy)
        self.publicPreference = np.array(publicPreference)
        self.theta = theta
    
    def updatePolicy(self, eliteInterest, publicInterest, theta):
        """
        Docstring for updatePolicy
        
        :param eliteInterest: the elite policy preference (npArray)
        :param publicInterest: the popular policy preference (npArray)
        :param theta: democratic responsiveness
        """
        # Ensure numpy arrays
        eliteInterest = np.array(eliteInterest)
        publicInterest = np.array(publicInterest)
        
        self.policy = theta * publicInterest + (1 - theta) * eliteInterest
        return self.policy
    
    def updatePublicPreference(self, originalPublicPref, policyOutcome, eta, noise):
        """
        Docstring for updatePublicPreerence
        
        :param originalPublicPref: np.Array: original public preference
        :param policyOutcome: np.Array: original policy outcome
        :param eta: double: learning rate
        :param noise: np.Array: jolts and noise
        """
        originalPublicPref = np.array(originalPublicPref)
        policyOutcome = np.array(policyOutcome)
        noise = np.array(noise)

        self.publicPreference = originalPublicPref + eta * (policyOutcome - originalPublicPref) + noise
        return self.publicPreference
    
    def updateTheta(self, eci, lambd):
        """
        Docstring for updateTheta

        :param eci: Double: elite caputure index
        :param lambd: Double: responsiveness to ECI

        return theta, which is a double
        """
        self.theta = self.theta - lambd * eci
        
        # CRITICAL FIX: Clamp theta between 0.0 and 1.0 to maintain model stability
        self.theta = np.clip(self.theta, 0.0, 1.0)
        
        return self.theta
