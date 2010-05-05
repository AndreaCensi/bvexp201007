import pickle
from pybv_experiments.analysis.olfaction_tensors import \
    analyze_olfaction_covariance_wrap


if __name__ == '__main__':
    files = [
        ('v_olfaction-random_pose_simulation.pickle', 'v_olfaction_'),
        ('v_olfaction_norm-random_pose_simulation.pickle', 'v_olfaction_norm_')
             ]

    path = ['olfaction_cov']
    for file, prefix in files:
        job = pickle.load(open(file))
        analyze_olfaction_covariance_wrap(job, path, prefix)
    
