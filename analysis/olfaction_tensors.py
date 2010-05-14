from numpy import array, linalg, square, sqrt, tile, ndarray, sum
import sys
import pickle
from pybv_experiments.visualization.saving import save_posneg_matrix, \
    get_filename
import pylab
from pybv.utils.misc import cov2corr
from numpy.lib.polynomial import polyfit, polyval, polyder
from numpy.lib.function_base import linspace
from numpy.core.numeric import dot
from pybv.utils.numpy_utils import gt, require_shape, square_shape
from report_tools.node import ReportNode
from report_tools.figures import MultiFigure
import numpy
from pybv_experiments.first_order.plot_parallel import create_report_figure_tensors


def create_distance_matrix(positions):
    ''' Returns the corresponding distance matrix 
        Position: 2 x n vector '''
    require_shape((2, gt(0)), positions)
    
    n = positions.shape[1]
    results = ndarray(shape=(n, n))

    for i in range(n):
        rep = tile(positions[:, i], (n, 1)).transpose()
        require_shape((2, n), rep)
        diff = positions - rep
        square(diff)
        distances = sqrt(sum(square(diff), axis=0))
        require_shape((n,), distances)
        results[i, :] = distances

    return results

def create_olfaction_Ttheta(positions, fder):
    '''
    positions: 2 x n  vector
    f_der: n x n
    '''
    require_shape((2, gt(0)), positions)
    n = positions.shape[1]
    require_shape((n, n), fder)
    
    results = ndarray(shape=(n, n))

    for i in range(n):
        J = array([ [0, -1], [1, 0]])
        Js = dot(J, positions[:, i])
        
        results[i, :] = dot(positions.transpose(), Js)

    results = results * fder # it IS element by element
    return results

def create_olfaction_Txy(positions, fder, distances):
    '''
    positions: 2 x n  vector
    f_der, distances: n x n
    
    returns Tx, Ty,   each n x n
    '''
    require_shape((2, gt(0)), positions)
    n = positions.shape[1]
    require_shape((n, n), fder)
    
    Tx = ndarray((n, n))
    Ty = ndarray((n, n))

    for i in range(n):
        rep = tile(positions[:, i], (n, 1)).transpose()
        require_shape((2, n), rep)
        diff = positions - rep
        
        Tx[i, :] = diff[0, :]
        Ty[i, :] = diff[1, :]
        
    # we add eps because otherwise 0/0 = NAN
    eps = 0.0001
    Tx = (Tx / (distances + eps)) * fder
    Ty = (Ty / (distances + eps)) * fder
    
    return Tx, Ty
    
    
    

def analyze_olfaction_covariance(covariance, receptors):
    ''' Covariance: n x n covariance matrix.
        Positions:  list of n  positions '''
    
    positions = [pose.get_2d_position() for pose, sens in receptors]
    positions = array(positions).transpose().squeeze()
    
    require_shape(square_shape(), covariance)
    n = covariance.shape[0]
    require_shape((2, n), positions)
    
    distances = create_distance_matrix(positions)
    correlation = cov2corr(covariance)
    flat_distances = distances.reshape(n * n) 
    flat_correlation = correlation.reshape(n * n)
    
    # let's fit a polynomial
    deg = 4
    poly = polyfit(flat_distances, flat_correlation, deg=deg)  
    
    knots = linspace(min(flat_distances), max(flat_distances), 2000)
    poly_int = polyval(poly, knots)
    
    poly_fder = polyder(poly)
    
    fder = polyval(poly_fder, distances)
    
    Ttheta = create_olfaction_Ttheta(positions, fder)
    Tx, Ty = create_olfaction_Txy(positions, fder, distances)
    
    
 
    fig1 = MultiFigure(id='cor-vs-distnace', caption='Estimated kernels',
                       shape=(3, 3))

    pylab.ioff()
    with fig1.attach_file('dist_vs_corr.png') as filename:
        pylab.figure()
        pylab.plot(flat_distances, flat_correlation, '.')
        pylab.plot(knots, poly_int, 'r-')
        pylab.xlabel('distance')
        pylab.ylabel('correlation')
        pylab.title('Correlation vs distance')
        pylab.legend(['data', 'interpolation deg = %s' % deg]) 
        pylab.savefig(filename)
        pylab.close()
    
    with fig1.attach_file('fder.png') as filename:
        pylab.figure()
        pylab.plot(knots, polyval(poly_fder, knots), 'r-')
        pylab.title('f der')
        pylab.savefig(filename)
        pylab.close() 
    
    with fig1.attach_file('distances.png') as f:
        save_posneg_matrix(f, distances)   
    fig1.add_subfigure('distances', caption='Distances')
     
    with fig1.attach_file('correlation.png') as f:
        save_posneg_matrix(f, correlation)   
    fig1.add_subfigure('correlation', caption='Correlation')
     
    with fig1.attach_file('covariance.png') as f:
        save_posneg_matrix(f, covariance)   
    fig1.add_subfigure('covariance', caption='covariance')
    
    with fig1.attach_file('f.png') as f:
        save_posneg_matrix(f, polyval(poly, distances))   
    fig1.add_subfigure('f', caption='f')
    
    with fig1.attach_file('fder.png') as f:
        save_posneg_matrix(f, fder)    
    fig1.add_subfigure('fder', caption='f der')
    
    T = numpy.zeros(shape=(3, Tx.shape[0], Tx.shape[1]))
    T[0, :, :] = Tx
    T[1, :, :] = Ty
    T[2, :, :] = Ttheta
    
    T_report = create_report_figure_tensors(T, report_id='tensors',
        caption="Predicted learned tensors")
    
    children = [fig1, T_report]
    return ReportNode(id='olfaction-theory', children=children)


def analyze_olfaction_covariance_job(job):
    P = job.result.cov_sensels
    receptors = job.vehicle.config.olfaction[0].receptors
    return analyze_olfaction_covariance(P, receptors)
 
