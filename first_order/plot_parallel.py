 
from pybv_experiments.visualization import save_posneg_matrix
from pybv.utils import cov2corr

def plot_tensors(state, conf_name, prefix=''):
    T = state.result.T
    Tx = T[0, :, :].squeeze()
    Ty = T[1, :, :].squeeze()
    Ttheta = T[2, :, :].squeeze()
    
    suite = 'first_order'
    save_posneg_matrix([conf_name, suite, prefix + 'Tx'], Tx)
    save_posneg_matrix([conf_name, suite, prefix + 'Ty'], Ty)
    save_posneg_matrix([conf_name, suite, prefix + 'Ttheta'], Ttheta)

    # normalize everything to the same absolute value
    maxvalue = abs(T).max()
    save_posneg_matrix([conf_name, suite, prefix + 'Tx_norm'], Tx, maxvalue=maxvalue)
    save_posneg_matrix([conf_name, suite, prefix + 'Ty_norm'], Ty, maxvalue=maxvalue)
    save_posneg_matrix([conf_name, suite, prefix + 'Ttheta_norm'], Ttheta, maxvalue=maxvalue)

def plot_covariance(state, conf_name):
    suite = 'covariance'
    covariance = state.result.cov_sensels
    save_posneg_matrix([conf_name, suite, 'covariance'], covariance)
    save_posneg_matrix([conf_name, suite, 'correlation'], cov2corr(covariance), maxvalue=1)
