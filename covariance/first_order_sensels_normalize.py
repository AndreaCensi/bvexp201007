from numpy import zeros
from pybv.utils import weighted_average, outer

class FirstorderSenselsNormalizeMean:

    def __init__(self, config):
        n = config.num_sensels
        k = config.num_commands        
        self.T = zeros((k, n, n))
        self.y_mean = zeros((n,))
        self.num_samples = 0
        
    def process_data(self, data):
        y = data.sensels
        y_dot = data.sensels_dot 
        u = data.commands 

        y_n = y - self.y_mean
        T = outer(u, outer(y_n, y_dot))

        self.T = weighted_average(self.T, self.num_samples, T)
        self.y_mean = weighted_average(self.y_mean, self.num_samples, y) 
        self.num_samples += 1
        

class Expectation:
    ''' A class to compute the mean of a quantity over time '''
    def __init__(self):
        self.num_samples = 0
        self.value = None
        
    def update(self, val):
        if not self.value:
            self.value = val
        else:
            self.value = weighted_average(self.value, self.num_samples, val) 
    
#    def get_value(self):
#        return self.value

class MeanCovariance:
    ''' Computes mean and covariance of a quantity '''
    def __init__(self):
        self.mean = Expectation()
        self.covariance = Expectation()


class FirstorderSenselsNormalizeUnif:

    def __init__(self, config):
        n = config.num_sensels
        k = config.num_commands        
        self.T = zeros((k, n, n))
        self.y_mean = 0
        self.num_samples = 0
        
    def process_data(self, data):        
        y = data.sensels
        y_dot = data.sensels_dot 
        u = data.commands 

        self.y_mean = weighted_average(self.y_mean, self.num_samples, y.mean()) 
        
        y_n = y - self.y_mean
        T = outer(u, outer(y_n, y_dot))

        #if self.num_samples > 50:
            # delay execution
        self.T = weighted_average(self.T, self.num_samples, T)
        self.num_samples += 1
        
