from pybv.utils import cov2corr
from reprep import Node

def create_report_covariance(state, report_id):
    covariance = state.result.cov_sensels
    
    report = Node(report_id)
    report.data('covariance', covariance)
    report.data('correlation', cov2corr(covariance))
    
    f = report.figure('matrices')
    f.sub('covariance', caption='Covariance matrix', display='posneg')
    f.sub('correlation', caption='Correlation matrix', display='posneg')
    
    return report

def create_report_figure_tensors(T, report_id, same_scale=False, caption=None):
    report = Node(report_id)
    f = report.figure('tensors', caption=caption)

    if same_scale:
        max_value = abs(T).max()
    else:
        max_value = None

    components = [(0, 'Tx', '$T_x$'),
                  (1, 'Ty', '$T_y$'),
                  (2, 'Ttheta', '$T_{\\theta}$')]
    
    for component, slice, caption in components:
        report.data(slice, T[component, :, :].squeeze())
        f.sub(slice, display='posneg', max_value=max_value)
    
    return report

def create_report_tensors(state, report_id):
    T = state.result.T
    vname = "" #TODO
    
    caption = '%s learned tensors, %d iterations' % \
        (vname, state.total_iterations)
    
    A = create_report_figure_tensors(T, same_scale=False, report_id='tensors',
        caption=caption)
    
    B = create_report_figure_tensors(T, same_scale=True, report_id='tensors-ss',
        caption='%s  (on the same scale)' % caption)
     
    report = Node(report_id)
    report.add_child(A)
    report.add_child(B)
    return report

 



    
