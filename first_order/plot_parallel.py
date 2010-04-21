 
from dynamic_tensor import *
from pybv_experiments.visualization import *
from pybv.simulation import load_state

def plot_tensors(result, job_id):
    T = result.T
    Tx = T[0,:,:].squeeze()
    Ty = T[1,:,:].squeeze()
    Ttheta = T[2,:,:].squeeze()
    
    suite = 'dynamic_tensor'

    save_posneg_matrix([suite, job_id, 'Tx'], Tx)
    save_posneg_matrix([suite, job_id, 'Ty'], Ty)
    save_posneg_matrix([suite, job_id, 'Ttheta'], Ttheta)

    # normalize everything to the same absolute value
    maxvalue = abs(T).max()
    save_posneg_matrix([suite, job_id, 'Tx_norm'], Tx, maxvalue=maxvalue)
    save_posneg_matrix([suite, job_id, 'Ty_norm'], Ty, maxvalue=maxvalue)
    save_posneg_matrix([suite, job_id, 'Ttheta_norm'], Ttheta, maxvalue=maxvalue)
