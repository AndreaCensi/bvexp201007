from pybv.utils.misc import outer, weighted_average
from numpy.linalg.linalg import pinv, LinAlgError
from numpy import dot, zeros
import pylab
from pybv_experiments.visualization.saving import  save_posneg_matrix
from numpy.lib.scimath import sqrt
import numpy 
import pickle
from compmake.structures import JobFailed
from report_tools.node import ReportNode
from pybv_experiments.first_order.plot_parallel import create_report_figure_tensors
from report_tools.figures import MultiFigure

class Expectation:
    ''' A class to compute the mean of a quantity over time '''
    def __init__(self, max_window=None):
        self.num_samples = 0
        self.value = None
        self.max_window = max_window
        
    def update(self, val):
        if  self.value is None:
            self.value = val
        else:
            self.value = weighted_average(self.value, self.num_samples, val) 
        self.num_samples += 1
        if self.max_window and self.num_samples > self.max_window:
            self.num_samples = self. max_window 
    
    def get_value(self):
        return self.value

class MeanCovariance:
    ''' Computes mean and covariance of a quantity '''
    def __init__(self, rcond=1e-3, max_window=None):
        self.mean_accum = Expectation(max_window)
        self.covariance_accum = Expectation(max_window)
        self.minimum = None
        self.maximum = None
        self.rcond = rcond
        self.information = None
        self.covariance = None
        self.mean = None
        
    def update(self, value):
        if  self.maximum is None:
            self.maximum = value
        else:
            self.maximum = numpy.maximum(value, self.maximum)
            
        if self.minimum is None:
            self.minimum = value
        else:
            self.minimum = numpy.minimum(value, self.minimum)
            
        self.mean_accum.update(value)
        self.mean = self.mean_accum.get_value()        
        value_norm = value - self.mean
        P = outer(value_norm, value_norm)
        self.covariance_accum.update(P)
        self.covariance = self.covariance_accum.get_value()
        try:
            self.information = pinv(self.covariance, rcond=1e-2)
        except LinAlgError:
            filename = 'pinv-failure'
            with  open(filename + '.pickle', 'w') as f:
                self.last_value = value
                pickle.dump(self, f)
            
            raise JobFailed('Did not converge; saved on %s' % filename)


class AffineModel:

    def __init__(self, config, max_window=None):
        # TODO: pass vehicle and not config
        self.y_dot_stats = MeanCovariance(max_window)
        self.y_stats = MeanCovariance(max_window)
        self.u_stats = MeanCovariance(max_window)
        self.T = Expectation(max_window)
        self.N = Expectation(max_window)
        # bilinear T
        self.bT = Expectation(max_window)
        # bilinear T, normalized
        self.bTn = Expectation(max_window)
        
    def process_data(self, data):        
        y = data.sensels
        y_dot = data.sensels_dot 
        u = data.commands 
#        n = y.shape[0]
#        k = u.shape[0]

        self.y_dot_stats.update(y_dot)
        self.y_stats.update(y)
        self.u_stats.update(u)
        
        y_norm = dot(self.y_stats.information, y - self.y_stats.mean)
        u_norm = dot(self.u_stats.information, u - self.u_stats.mean)
        
        # Assuming model of the form:
        # 
        # y_dot = mu + M y  + N u + T(y,u)
        # 
        # assuming that mu = 0 and M = 0
        # 
        # Then:  
        #   N = E{ y_dot u~ }

        Ns = outer(y_dot, u_norm)
        self.N.update(Ns)
        N = self.N.get_value()
        
        Nu = dot(N, u)
        Ts = outer(u_norm, outer(y_norm, y_dot - Nu))        
        self.T.update(Ts)

        # this assumes the normal bilinear model 
        bT = outer(u_norm, outer(y - self.y_stats.mean, y_dot))        
        self.bT.update(bT)

        # this assumes the normal bilinear model 
        bTn = outer(u_norm, outer(y_norm, y_dot))        
        self.bTn.update(bTn)

def create_report_affine(state, report_id):
    y_dot_mean = state.result.y_dot_stats.mean
    y_dot_cov = state.result.y_dot_stats.covariance
    y_dot_inf = state.result.y_dot_stats.information
    y_dot_min = state.result.y_dot_stats.minimum
    y_dot_max = state.result.y_dot_stats.maximum
    
    y_mean = state.result.y_stats.mean
    y_cov = state.result.y_stats.covariance
    y_inf = state.result.y_stats.information
    y_min = state.result.y_stats.minimum
    y_max = state.result.y_stats.maximum
    
    u_mean = state.result.u_stats.mean
    u_inf = state.result.u_stats.information
    u_cov = state.result.u_stats.covariance
    
    N = state.result.N.get_value()
     
    
    report_y_dot = create_report_var(name='y_dot', \
                              mean=y_dot_mean, cov=y_dot_cov, inf=y_dot_inf, \
                              minimum=y_dot_min, maximum=y_dot_max)  
    
    report_y = create_report_var(name='y', \
                              mean=y_mean, cov=y_cov, inf=y_inf,
                              minimum=y_min, maximum=y_max)
    
    report_u = create_report_var(name='u', \
                              mean=u_mean, cov=u_cov, inf=u_inf)
    
    T = state.result.T.get_value()
    report_T = create_report_figure_tensors(T, report_id='T',
                                            caption='Learned T')
    
    with report_T.attach_file('N.png') as filename:        
        pylab.ioff()
        f = pylab.figure()
        for i in range(N.shape[1]):
            v = N[:, i].squeeze()
            pylab.plot(v)
    
        pylab.savefig(filename)
        pylab.close(f)
        
    report_T.add_subfigure('N', caption='Linear part')

    bT = state.result.bT.get_value()
    report_bT = create_report_figure_tensors(bT, report_id='bT',
                                            caption='Learned bT')
    
    bTn = state.result.bTn.get_value()
    report_bTn = create_report_figure_tensors(bTn, report_id='bTn',
                                            caption='Learned bTn')
    
    
    node = ReportNode(id=report_id)
    node.children = [report_y, report_y_dot, report_u, report_T, report_bT,
                    report_bTn]
    return node

def create_report_var(name, mean, cov, inf, minimum=None, maximum=None):
    
    figure = MultiFigure(id=name, nodeclass='var')

    with figure.attach_file('covariance.png') as filename:        
        save_posneg_matrix(filename, cov)

    with figure.attach_file('information.png') as filename:        
        save_posneg_matrix(filename, inf)

    with figure.attach_file('mean.png') as filename:        
        e = 3 * sqrt(cov.diagonal())
        pylab.ioff()    
        f = pylab.figure()
        x = range(len(mean))
        pylab.errorbar(x, mean, yerr=e)
        if minimum is not None:
            pylab.plot(x, minimum, 'b-')
        if maximum is not None:
            pylab.plot(x, maximum, 'b-')
        pylab.savefig(filename)
        pylab.close(f)
    
    figure.add_subfigure('mean', caption='Mean')
    figure.add_subfigure('covariance', caption='Covariance')
    figure.add_subfigure('information', caption='Information')

    return figure
