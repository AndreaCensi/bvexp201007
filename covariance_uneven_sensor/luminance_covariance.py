import numpy
from bv.utils import weighted_average

class LuminanceCovariance:

    def __init__(self, config):
        n = config.optics.num_photoreceptors
        self.cov_luminance = numpy.zeros((n,n))
        self.mean_luminance = numpy.zeros((n,1))
        self.num_samples = 0
        
    def update(self, data):
        # Get the data as a column vector
        y = ascolumn( data.optics.luminance )
        # Update mean estimate
        self.mean_luminance = weighted_average(self.mean_luminance, self.num_samples, y)
        # Substract the mean
        yn = y - self.mean_luminance
        # Compute the exterior product of normalized luminance
        yy = numpy.dot(yn, yn.transpose())
        # Update covariance estimate
        self.cov_luminance = weighted_average(self.cov_luminance, self.num_samples, yy ) 
        # Keep track of how many we integrated so far
        self.num_samples += 1
        
    def final_computation(self):
        # no final computation defined for this one
        pass
        
    def parallel_merge(self, that):
        """ Support function for parallel implementation of the simulation """
        self.cov_luminance = weighted_average(self.cov_luminance, self.num_samples, that.cov_luminance, that.num_samples)
        self.mean_luminance = weighted_average(self.mean_luminance, self.num_samples, that.mean_luminance, that.num_samples)        
        self.num_samples += that.num_samples
        
    