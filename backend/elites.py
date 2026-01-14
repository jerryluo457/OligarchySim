# elites.py
import numpy as np

class Elites:

    def __init__(self, eliteInfoDict):
        """
        Docstring for __init__
        
        :param elictInfoDict: dict, contains elitePoints, weights.
        
        The key of each element is optimal point for each elite, assumed to be constant.
        The value of each element is the numeric representation of how much influence each elite has (the weight).
        """

        self.eliteInfoDict = eliteInfoDict
        # Convert keys to list of lists/tuples first to ensure 2D array structure
        self.elitePrefenceList = np.array(list(eliteInfoDict.keys())) 
        self.eliteInfluenceList = np.array(list(eliteInfoDict.values()))

    def computeEliteCentroid(self):
        centroid = np.average(self.elitePrefenceList, axis=0, weights=self.eliteInfluenceList)
        return centroid
        
    def updateWeights(self, weights, elitePoints, outcome, kappa):
            weights = np.array(weights)
            elitePoints = np.array(elitePoints)
            outcome = np.array(outcome)

            # compute Euclidean distance in policy space
            distances = np.linalg.norm(elitePoints - outcome, axis=1)

            # Update weights based on proximity (success reinforces influence)
            unnormalized = weights * np.exp(-kappa * distances)
                
            total = np.sum(unnormalized)
            
            # Avoid division by zero if weights collapse
            if total == 0:
                self.eliteInfluenceList = np.ones_like(weights) / len(weights)
            else:
                self.eliteInfluenceList = unnormalized / total  # normalize
                
            return self.eliteInfluenceList