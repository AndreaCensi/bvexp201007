from pybv.simulation import list_available_states, get_computations_root, load_state
import scipy.io
import os

jobs = {}
for job in list_available_states():
    jobs[job] = load_state(job)
    
    
filename = os.path.join(get_computations_root(), 'all_jobs.mat')

scipy.io.savemat(filename, jobs)
