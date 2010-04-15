from numpy import zeros, dot
from pybv.utils import weighted_average, ascolumn, outer

class ReadingsCovariance:

    def __init__(self, config):
        n = config.rangefinder[0].num_readings
        self.cov_readings = zeros((n,n))
        self.mean_readings = zeros((n,1))
        self.num_samples = 0
        
    def process_data(self, data):
        y = data.rangefinder[0].readings
        self.mean_readings = weighted_average(self.mean_readings, self.num_samples, y)
        yn = y - self.mean_readings
        T = outer( yn, yn )
        self.cov_readings = weighted_average(self.cov_readings, self.num_samples, T ) 
        self.num_samples += 1
        
    # def parallel_merge(self, that):
    #     """ Support function for parallel implementation of the simulation """
    #     self.cov_readings = weighted_average(self.cov_readings, self.num_samples, that.cov_readings, that.num_samples)
    #     self.mean_readings = weighted_average(self.mean_readings, self.num_samples, that.mean_readings, that.num_samples)        
    #     self.num_samples += that.num_samples
    #     
