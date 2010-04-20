 
from dynamic_tensor import *
from pybv_experiments.visualization import *
from pybv.simulation import load_state

jobs = ['firstorder_distance_nonuniform',   'firstorder_luminance_nonuniform',
'firstorder_distance_uniform',  'firstorder_luminance_uniform',
 'firstorder_polarized','firstorder_olfaction']

suite = 'dynamic_tensor'

for job_id in jobs:
    state = load_state(job_id)
    T = state.result.T
    Tx = T[0,:,:].squeeze()
    Ty = T[1,:,:].squeeze()
    Ttheta = T[2,:,:].squeeze()
    
    save_posneg_matrix([suite, job_id, 'Tx'], Tx)
    save_posneg_matrix([suite, job_id, 'Ty'], Ty)
    save_posneg_matrix([suite, job_id, 'Ttheta'], Ttheta)

    # normalize everything to the same absolute value
    maxvalue = abs(T).max()
    save_posneg_matrix([suite, job_id, 'Tx_norm'], Tx, maxvalue=maxvalue)
    save_posneg_matrix([suite, job_id, 'Ty_norm'], Ty, maxvalue=maxvalue)
    save_posneg_matrix([suite, job_id, 'Ttheta_norm'], Ttheta, maxvalue=maxvalue)
