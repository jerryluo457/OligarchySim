# elites.py
import numpy as np

class Elites:
    def __init__(self, elite_list):
        """
        :param elite_list: list of dicts [{'name': str, 'x': float, 'y': float, 'weight': float}, ...]
        """
        self.elite_data = elite_list
        
        # Extract arrays for computation
        if len(elite_list) > 0:
            self.positions = np.array([[e['x'], e['y']] for e in elite_list])
            self.weights = np.array([e['weight'] for e in elite_list])
            self.names = [e['name'] for e in elite_list]
        else:
            self.positions = np.array([])
            self.weights = np.array([])
            self.names = []

    def computeEliteCentroid(self):
        if len(self.weights) == 0:
            return np.array([0.0, 0.0])
            
        # Weighted Average
        # We re-normalize weights for the centroid calculation if they drift
        total_weight = np.sum(self.weights)
        if total_weight == 0:
            return np.array([0.0, 0.0])
            
        centroid = np.average(self.positions, axis=0, weights=self.weights)
        return centroid
    
    def updateWeights(self, weights, elitePoints, outcome, kappa):
        # We pass current_weights back in to keep state consistent across steps
        weights = np.array(weights)
        outcome = np.array(outcome)

        # Euclidean distance in policy space
        distances = np.linalg.norm(elitePoints - outcome, axis=1)

        # Update weights (closer elites gain power)
        unnormalized = weights * np.exp(-kappa * distances)
        
        total = np.sum(unnormalized)
        if total == 0:
             self.weights = weights 
        else:
             self.weights = unnormalized / total
             
        return self.weights