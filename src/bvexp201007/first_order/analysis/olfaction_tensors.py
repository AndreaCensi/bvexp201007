from numpy import array, square, sqrt, tile, ndarray, sum
import pylab
from pybv.utils.misc import cov2corr
from numpy.lib.polynomial import polyfit, polyval, polyder
from numpy.lib.function_base import linspace
from numpy.core.numeric import dot
from pybv.utils.numpy_utils import gt, require_shape, square_shape

import numpy
from pybv_experiments.first_order.plot_parallel import create_report_figure_tensors
from reprep import Node


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
    
    positions = [pose.get_2d_position() for pose, sens in receptors] #@UnusedVariable
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
    
    
    report = Node('olfaction-theory')
    report.data('flat_distances', flat_distances)
    report.data('flat_correlation', flat_correlation)
    
    
    with report.data_file('dist_vs_corr', 'image/png') as filename:
        pylab.figure()
        pylab.plot(flat_distances, flat_correlation, '.')
        pylab.plot(knots, poly_int, 'r-')
        pylab.xlabel('distance')
        pylab.ylabel('correlation')
        pylab.title('Correlation vs distance')
        pylab.legend(['data', 'interpolation deg = %s' % deg]) 
        pylab.savefig(filename)
        pylab.close()
    
    with report.data('fder', fder).data_file('fder', 'image/png') as filename:
        pylab.figure()
        pylab.plot(knots, polyval(poly_fder, knots), 'r-')
        pylab.title('f der')
        pylab.savefig(filename)
        pylab.close() 
    
    report.data('distances', distances)
    report.data('correlation', correlation)
    report.data('covariance', covariance)
    report.data('f', polyval(poly, distances))   
    
    
    
    f = report.figure(id='cor-vs-distnace', caption='Estimated kernels',
                       shape=(3, 3))
    f.sub('dist_vs_corr')
    f.sub('fder')
    f.sub('f', display='scale')
    f.sub('distances', display='scale')
    f.sub('correlation', display='posneg')
    f.sub('covariance', display='posneg')
    
    T = numpy.zeros(shape=(3, Tx.shape[0], Tx.shape[1]))
    T[0, :, :] = Tx
    T[1, :, :] = Ty
    T[2, :, :] = Ttheta
    
    T_report = create_report_figure_tensors(T, report_id='tensors',
        caption="Predicted learned tensors")
    
    report.add_child(T_report)

    return report


def analyze_olfaction_covariance_job(job):
    P = job.result.cov_sensels
    receptors = job.vehicle.config.olfaction[0].receptors
    return analyze_olfaction_covariance(P, receptors)
 
