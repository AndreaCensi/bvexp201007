
import go # make sure everything ran

from luminance_covariance import *
from pybv_experiments.visualization import *
from pybv.simulation import load_state

for job_id in ['covariance_luminance_nonuniform', 'covariance_luminance_uniform']:
    state = load_state(job_id)
    covariance = state.result.cov_luminance
    save_posneg_matrix(['covariance', job_id, 'cov_luminance'], covariance)

from sensel_covariance import *

for job_id in ['covariance_sensels_nonuniform', 'covariance_sensels_uniform']:
    state = load_state(job_id)
    covariance = state.result.cov_sensels
    save_posneg_matrix(['covariance', job_id, 'cov_sensels'], covariance)

from readings_covariance import *

for job_id in ['covariance_readings_nonuniform', 'covariance_readings_uniform']:
    state = load_state(job_id)
    covariance = state.result.cov_readings
    save_posneg_matrix(['covariance', job_id, 'cov_readings'], covariance)

    
# 
# from pybv.visualization import plot_covariance
# from pylab import *
# figure()
# 
# plot_covariance(result.result_sensels.cov_sensels)
# 
# 
# figure()
# plot_covariance(result.result_luminance.cov_luminance, result.vehicle2.config.optics[0].directions)
# 
# figure()
# plot_covariance(result.result_readings.cov_readings, sensor.directions)
# 
# 
