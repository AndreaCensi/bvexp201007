from copy import deepcopy

def normalize_tensor(result_covariance, result_firstorder):
    covariance = result_covariance.result.cov_sensels
    T = result_firstorder.result.T
    
    state = deepcopy(result_firstorder)
    state.result.T = -T
    # TODO complete this!!
    return state
