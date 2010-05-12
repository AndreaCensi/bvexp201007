from copy import deepcopy
from numpy import linalg, tensordot

def normalize_tensor(result_covariance, result_firstorder, rcond=1e-2):
    covariance = result_covariance.result.cov_sensels
    T = result_firstorder.result.T
    
    inv_covariance = linalg.pinv(covariance, rcond=rcond)
    Tnorm = -tensordot(T, inv_covariance, axes=(1, 1))
    
    state = deepcopy(result_firstorder)
    state.result.T = Tnorm
    state.result.inv_covariance = inv_covariance

    return state
