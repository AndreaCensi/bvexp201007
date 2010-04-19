from numpy import zeros, dot
from pybv.utils import weighted_average, ascolumn, outer

class SenselCovariance:

    def __init__(self, config):
        n = config.num_sensels
        self.cov_sensels = zeros((n,n))
        self.mean_sensels = zeros((n,))
        self.num_samples = 0
        
    def process_data(self, data):
        y = data.sensels
        self.mean_sensels = weighted_average(self.mean_sensels, self.num_samples, y)
        yn = y - self.mean_sensels
        T = outer(yn, yn)
        self.cov_sensels = weighted_average(self.cov_sensels, self.num_samples, T ) 
        self.num_samples += 1
