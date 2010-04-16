
import go # make sure everything ran

from dynamic_tensor import *
from pybv_experiments.visualization import *
from pybv.simulation import load_state

jobs = ['firstorder_distance_nonuniform',   'firstorder_luminance_nonuniform',
'firstorder_distance_uniform',      'firstorder_luminance_uniform']

for job_id in jobs:
    state = load_state(job_id)
    T = state.result.T
    Tx = T[0,:,:].squeeze()
    Ty = T[1,:,:].squeeze()
    Ttheta = T[2,:,:].squeeze()
    save_posneg_matrix(['dynamic_tensor', job_id, 'Tx'], Tx)
    save_posneg_matrix(['dynamic_tensor', job_id, 'Ty'], Ty)
    save_posneg_matrix(['dynamic_tensor', job_id, 'Ttheta'], Ttheta)
