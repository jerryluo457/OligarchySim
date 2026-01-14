# state.py
import numpy as np

class State:
    def __init__(self, M, E, O, w, theta, t):
        """
        Docstring for constructor
        
        :param M: Median-voter public preference, function of t
        :param E: Elite centroid (elites weighted preference), function of t
        :param O: Policy outcome, function of t
        :param w: List of elite weights, vector function of t 
        :param theta: Democratic responsiveness, or the public's weight in decision waiting
        :param t: timestamp (measured in political cycles)
        """
        self.M = np.array(M)
        self.E = np.array(E)
        self.O = np.array(O)
        self.w = np.array(w)
        self.theta = theta
        self.t = t
    
    # accessor methods
    def getMedVoterPref(self):
        return self.M

    def getEliteCentroid(self):
        return self.E

    def getPolicyOutcome(self):
        return self.O

    def getEliteWeights(self):
        return self.w

    def getDemResponsv(self):
        return self.theta
