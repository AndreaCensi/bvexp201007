from numpy import zeros, dot
from pybv.utils import weighted_average, ascolumn, outer

class LuminanceCovariance:

    def __init__(self, config):
        n = config.optics[0].num_photoreceptors
        self.cov_luminance = zeros((n,n))
        self.mean_luminance = zeros((n,1))
        self.num_samples = 0
        
    def process_data(self, data):
        y = data.optics[0].luminance
        # Update mean estimate
        self.mean_luminance = weighted_average(self.mean_luminance, self.num_samples, y)
        # Subtract the mean
        yn = y - self.mean_luminance
        # Compute the exterior product of normalized luminance
        T = outer(yn, yn)
        # Update covariance estimate
        self.cov_luminance = weighted_average(self.cov_luminance, self.num_samples, T ) 
        # Keep track of how many we integrated so far
        self.num_samples += 1
        
    def parallel_merge(self, that):
        """ Support function for parallel implementation of the simulation """
        self.cov_luminance = weighted_average(self.cov_luminance, self.num_samples, that.cov_luminance, that.num_samples)
        self.mean_luminance = weighted_average(self.mean_luminance, self.num_samples, that.mean_luminance, that.num_samples)        
        self.num_samples += that.num_samples
        
    