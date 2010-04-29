from numpy import zeros 
from pybv.utils import weighted_average, outer

class LuminanceCovariance:

    def __init__(self, config):
        n = config.optics[0].num_photoreceptors
        # Initialize a n x n matrix of zeros
        self.cov_luminance = zeros((n, n))
        # Initialize a n-vector of zero
        self.mean_luminance = zeros((n,))
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
        self.cov_luminance = weighted_average(self.cov_luminance, self.num_samples, T) 
        # Keep track of how many we integrated so far
        self.num_samples += 1
        

