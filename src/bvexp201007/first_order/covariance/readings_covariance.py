from numpy import zeros
from pybv.utils import weighted_average, outer

class ReadingsCovariance:
    
    def __init__(self, config):
        n = config.rangefinder[0].num_readings
        self.cov_readings = zeros((n, n))
        self.mean_readings = zeros((n,))
        self.num_samples = 0
        
    def process_data(self, data):
        y = data.rangefinder[0].readings
        self.mean_readings = weighted_average(self.mean_readings, self.num_samples, y)
        yn = y - self.mean_readings
        T = outer(yn, yn)
        self.cov_readings = weighted_average(self.cov_readings, self.num_samples, T) 
        self.num_samples += 1
        
