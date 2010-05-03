from pybv.utils.misc import outer, weighted_average
from numpy.linalg.linalg import pinv
from numpy import dot
import pylab
from pybv_experiments.visualization.saving import get_filename, save_posneg_matrix
from numpy.lib.scimath import sqrt
import numpy

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
        self.information = pinv(self.covariance)


class AffineModel:

    def __init__(self, config):
        max_window = 1000 
        # TODO: pass vehicle and not config
        self.y_dot_stats = MeanCovariance(max_window)
        self.y_stats = MeanCovariance(max_window)
        self.u_stats = MeanCovariance(max_window)
        self.T = Expectation(max_window)
        self.N = Expectation(max_window)
        
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


def affine_plot(state, path, prefix=''):
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
    T = state.result.T.get_value()
 
    plot_var_stats(path, name=prefix + 'y_dot', \
                              mean=y_dot_mean, cov=y_dot_cov, inf=y_dot_inf, \
                              minimum=y_dot_min, maximum=y_dot_max)
    
    plot_var_stats(path, name=prefix + 'y', \
                              mean=y_mean, cov=y_cov, inf=y_inf,
                              minimum=y_min, maximum=y_max)
    
    plot_var_stats(path, name=prefix + 'u', \
                              mean=u_mean, cov=u_cov, inf=u_inf)
    
    
    # plot tensor T
    Tx = T[0, :, :].squeeze()
    Ty = T[1, :, :].squeeze()
    Ttheta = T[2, :, :].squeeze()
    save_posneg_matrix(path + [prefix + 'Tx'], Tx)
    save_posneg_matrix(path + [prefix + 'Ty'], Ty)
    save_posneg_matrix(path + [prefix + 'Ttheta'], Ttheta)
 
    # plot tensor N
    
    filename = get_filename(path + [prefix + 'N'], 'png')
    
    pylab.ioff()
    f = pylab.figure()
    for i in range(N.shape[1]):
        v = N[:, i].squeeze()
        pylab.plot(v)

    pylab.savefig(filename)
    pylab.close(f)

    
    
    tex = """
        \\subimport{.}{tex1}
        \\subimport{.}{tex2}
        \\subimport{.}{tex3}
        
        \\begin{figure}[h!]
        \\setlength\\fboxsep{0pt} 
        \\caption{\\label{fig:figure_label} figure_caption  }
        
        \\subfloat[cap1]{
            \\fbox{\\includegraphics[height=image_height]{pic1}}
        }
        \\hfill
        \\subfloat[cap2]{
            \\fbox{\\includegraphics[height=image_height]{pic2}}
        }
        \\hfill
        \\subfloat[cap3]{
            \\fbox{\\includegraphics[height=image_height]{pic3}}
        }
        \\hfill
        \\subfloat[cap4]{
            \\fbox{\\includegraphics[height=image_height]{pic4}}
        }
        \\end{figure}
        
        
        """
    sub = {
           'image_height': '2.5cm',
           'figure_label': 'unknown',
           'figure_caption': '...',
        'tex1': prefix + 'y.tex',
        'tex2': prefix + 'y_dot.tex',
        'tex3': prefix + 'u.tex',
        'pic1': prefix + 'N',
        'pic2': prefix + 'Tx',
        'pic3': prefix + 'Ty',
        'pic4': prefix + 'Ttheta',
        
    }

    #sub.update(**kwargs)
    for k, v in sub.items():
        tex = tex.replace(k, v)

    tex_filename = get_filename(path + [prefix + 'index'], 'tex')
    with open(tex_filename, 'w') as f:
        f.write(tex)


def plot_var_stats(path, name, mean, cov, inf, minimum=None, maximum=None):
    '''Writes on path/name.tex'''
    
    save_posneg_matrix(path + [name + '_covariance'], cov)
    save_posneg_matrix(path + [name + '_information'], inf)

    filename = get_filename(path + [name + '_mean'], 'png')
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
    
    tex_filename = get_filename(path + [name], 'tex')

    tex = """
    \\begin{figure}[h!]
        \\setlength\\fboxsep{0pt} 
        \\caption{\\label{fig:figure_label} figure_caption  }
        
        \\subfloat[cap1]{
            \\fbox{\\includegraphics[height=image_height]{pic1}}
        }
        \\hfill
        \\subfloat[cap2]{
            \\fbox{\\includegraphics[height=image_height]{pic2}}
        }
        \\hfill
        \\subfloat[cap3]{
            \\fbox{\\includegraphics[height=image_height]{pic3}}
        }
         
    \\end{figure}
"""
    sub = {'image_height': '2.5cm', 'figure_label': 'unknown',
            'figure_caption': 'Statistics for %s' % tex_friendly(name),
           'pic1': name + '_mean', 'cap1': 'mean',
           'pic2': name + '_covariance', 'cap2': 'covariance',
           'pic3': name + '_information', 'cap3': 'information',
           }
    
    #sub.update(**kwargs)
    for k, v in sub.items():
        tex = tex.replace(k, v)

    with open(tex_filename, 'w') as f:
        f.write(tex)


def tex_friendly(s):
    ''' escapes a string to tex '''
    # TODO: many more other substitutions
    return s.replace('_', '-')
    
    
