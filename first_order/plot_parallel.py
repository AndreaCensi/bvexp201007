from pybv_experiments.visualization import save_posneg_matrix
from pybv.utils import cov2corr
from pybv_experiments.visualization.saving import get_filename

def plot_tensors(state, path, prefix=''):
    T = state.result.T
    Tx = T[0, :, :].squeeze()
    Ty = T[1, :, :].squeeze()
    Ttheta = T[2, :, :].squeeze()
    
    save_posneg_matrix(path + [prefix + 'Tx'], Tx)
    save_posneg_matrix(path + [prefix + 'Ty'], Ty)
    save_posneg_matrix(path + [prefix + 'Ttheta'], Ttheta)

    # normalize everything to the same absolute value
    maxvalue = abs(T).max()
    save_posneg_matrix(path + [prefix + 'Tx_samescale'], Tx, maxvalue=maxvalue)
    save_posneg_matrix(path + [prefix + 'Ty_samescale'], Ty, maxvalue=maxvalue)
    save_posneg_matrix(path + [prefix + 'Ttheta_samescale'], Ttheta,
                       maxvalue=maxvalue)

def plot_tensors_tex(path, prefix='', **kwargs):
    ''' Creates support TeX files for displaying the images 
        created by plot_tensors(). 
    
    Arguments:
    
        path, prefix:  the arguments you gave to plot_tensors
        
    Optional arguments:
    
        label, caption, image_width
    '''
    tex = """
    \begin{figure}
        \setlength\fboxsep{0pt} 
        \caption{\label{fig:label} caption  }
        \hfill        
        \subfloat[cap1]{\fbox{\includegraphics[width=image_width]{pic1}}}
        \hfill
        \subfloat[cap2]{\fbox{\includegraphics[width=image_width]{pic2}}}
        \hfill    
        \subfloat[cap3]{\fbox{\includegraphics[width=image_width]{pic3}}}
        \hfill 
    \end{figure}
"""
    sub = {'image_width': '3cm', 'label': 'unknown', 'caption': '',
           'cap1': '$T_x$', 'cap2': '$T_y$', 'cap3':'$T_\\theta$',
           'pic1': prefix + 'Tx', 'pic2': prefix + 'Ty', 'pic3': prefix + 'Ttheta'}
    sub.update(**kwargs)
    for k, v in sub.items():
        tex = tex.replace(k, v)

    filename = get_filename(path + [prefix + 'tensors'], 'tex')
    with open(filename, 'w') as f:
        f.write(tex)
        
    

def plot_covariance(state, path, prefix=''):
    covariance = state.result.cov_sensels
    save_posneg_matrix(path + [prefix + 'covariance'], covariance)
    save_posneg_matrix(path + [prefix + 'correlation'], cov2corr(covariance), maxvalue=1)
    
    
def plot_covariance_tex(path, prefix='', **kwargs):
    ''' Creates support TeX files for displaying the images 
        created by plot_covariance(). 
    
    Arguments:
    
        path, prefix:  the arguments you gave to plot_tensors
        
    Optional arguments:
    
        label, caption, image_width
    '''
    tex = """
    \begin{figure}
        \setlength\fboxsep{0pt} 
        \caption{\label{fig:label} Correlation  }
        
        \fbox{\includegraphics[width=image_width]{pic1}}
         
    \end{figure}
"""
    sub = {'image_width': '3cm', 'label': 'unknown', 'caption': '',
           'pic1': prefix + 'correlation'}
    
    sub.update(**kwargs)
    for k, v in sub.items():
        tex = tex.replace(k, v)

    filename = get_filename(path + [prefix + 'covariance'], 'tex')
    with open(filename, 'w') as f:
        f.write(tex)
        
    
