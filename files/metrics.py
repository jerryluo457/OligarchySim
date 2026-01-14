# metrics.py
import numpy as np

def eliteCaptureIndex(publicPref, eliteCentroid, policyOutcome):
    publicPref = np.array(publicPref)
    eliteCentroid = np.array(eliteCentroid)
    policyOutcome = np.array(policyOutcome)

    numerator = np.linalg.norm(policyOutcome - publicPref)
    denominator = np.linalg.norm(eliteCentroid - publicPref) + 0.0001  # 0.0001 prevents div by 0 error. 
    # We will try to prevent the public preference from becoming the elite centroid

    return numerator / denominator

def policyDistance(a, b):
    """
    Docstring for policyDistance
    
    :param a: np.Array of dimension d
    :param b: np.Array of dimension d
    """
    a = np.array(a)
    b = np.array(b)
    return np.linalg.norm(a - b)
