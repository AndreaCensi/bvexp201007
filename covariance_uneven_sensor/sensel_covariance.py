from numpy import zeros, dot
from pybv.utils import weighted_average, ascolumn

class SenselCovariance:

    def __init__(self, config):
        n = config.num_sensels
        self.cov_sensels = zeros((n,n))
        self.mean_sensels = zeros((n,1))
        self.num_samples = 0
        
    def process_data(self, data):
        y = ascolumn( data.sensels )
        self.mean_sensels = weighted_average(self.mean_sensels, self.num_samples, y)
        yn = y - self.mean_sensels
        yy = dot(yn, yn.transpose())
        self.cov_sensels = weighted_average(self.cov_sensels, self.num_samples, yy ) 
        self.num_samples += 1
