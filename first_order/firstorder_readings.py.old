from numpy import zeros, dot, multiply
from pybv.utils import weighted_average, ascolumn, outer

class FirstorderDistance:

    def __init__(self, config):
        n = config.rangefinder[0].num_readings
        k = config.num_commands        
        self.num_samples = 0
        self.T = zeros((k,n,n))
        
    def process_data(self, data):
        y     = data.rangefinder[0].readings
        y_dot = data.rangefinder[0].readings_dot 
        u     = data.commands 

        T     = outer( u, outer(y, y_dot) )

        self.T = weighted_average(self.T, self.num_samples, T ) 
        self.num_samples += 1
        
