
import go # make sure everything ran

from luminance_covariance import *
from pybv_experiments.visualization import *
from pybv.simulation import load_state
from pybv.utils import cov2corr

suite = 'covariance'

for job_id in ['covariance_luminance_nonuniform', 'covariance_luminance_uniform']:
    state = load_state(job_id)
    covariance = state.result.cov_luminance
    save_posneg_matrix([suite, job_id, 'covariance'], covariance)
    save_posneg_matrix([suite, job_id, 'correlation'], cov2corr(covariance), maxvalue=1)

from sensel_covariance import *

for job_id in ['covariance_sensels_nonuniform', 'covariance_sensels_uniform', 'covariance_olfaction']:
    state = load_state(job_id)
    covariance = state.result.cov_sensels
    save_posneg_matrix([suite, job_id, 'covariance'], covariance)
    save_posneg_matrix([suite, job_id, 'correlation'], cov2corr(covariance),maxvalue=1)

from readings_covariance import *

for job_id in ['covariance_distance_nonuniform', 'covariance_distance_uniform']:
    state = load_state(job_id)
    covariance = state.result.cov_readings
    save_posneg_matrix([suite, job_id, 'covariance'], covariance)
    save_posneg_matrix([suite, job_id, 'correlation'], cov2corr(covariance),maxvalue=1)

