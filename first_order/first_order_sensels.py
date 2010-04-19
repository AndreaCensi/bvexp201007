from numpy import zeros, dot, multiply
from pybv.utils import weighted_average, outer

class FirstorderSensels:

    def __init__(self, config):
        n = config.num_sensels
        k = config.num_commands        
        self.T = zeros((k,n,n))
        self.num_samples = 0
        
    def process_data(self, data):
        y     = data.sensels
        y_dot = data.sensels_dot 
        u     = data.commands 

        T     = outer( u, outer(y, y_dot) )

        self.T = weighted_average(self.T, self.num_samples, T ) 
        self.num_samples += 1
        
