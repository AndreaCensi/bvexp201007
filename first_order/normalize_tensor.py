from pybv.utils import OpenStruct

def normalize_tensor(depends):
    covariance = depends[0].result.cov_sensels
    T = depends[1].result.T
    
    state = OpenStruct()
    state.result = OpenStruct()
    state.result.T = -T
    
    return state