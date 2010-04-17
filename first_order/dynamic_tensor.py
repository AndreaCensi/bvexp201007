from numpy import zeros, dot, multiply
from pybv.utils import weighted_average, ascolumn, outer

class DynamicTensor:

    def __init__(self, config):
        n = config.optics[0].num_photoreceptors
        k = config.num_commands        
        self.num_samples = 0
        self.T = zeros((k,n,n))
        
    def process_data(self, data):
        y     = data.optics[0].luminance
        y_dot = data.optics[0].luminance_dot 
        u     = data.commands 

        T     = outer( u, outer(y, y_dot) )

        self.T = weighted_average(self.T, self.num_samples, T ) 
        self.num_samples += 1
        
