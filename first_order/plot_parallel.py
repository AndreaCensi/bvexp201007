from pybv_experiments.visualization import save_posneg_matrix
from pybv.utils import cov2corr
from report_tools.figures import MultiFigure
from report_tools.node import ReportNode

def create_report_covariance(state, report_id):
    covariance = state.result.cov_sensels
    vname = ""
    
    figure = MultiFigure(id=report_id, nodeclass='covariance',
                        caption='Covariance %s' % vname)
    
    with figure.attach_file('covariance.png') as f:
        save_posneg_matrix(f, covariance)

    with figure.attach_file('correlation.png') as f:
        save_posneg_matrix(f, cov2corr(covariance), maxvalue=1)

    figure.add_subfigure('covariance', caption='Covariance')
    figure.add_subfigure('correlation', caption='Correlation')
    
    return figure

def create_report_figure_tensors(T, report_id, same_scale=False, caption=None):
    figure = MultiFigure(id=report_id, nodeclass='tensors', caption=caption)

    if same_scale:
        maxvalue = abs(T).max()
    else:
        maxvalue = None

    components = [(0, 'Tx', '$T_x$'),
                  (1, 'Ty', '$T_y$'),
                  (2, 'Ttheta', '$T_{\\theta}$')]
    
    for component, figname, caption in components:
        with figure.attach_file('%s.png' % figname) as f:
            save_posneg_matrix(f, T[component, :, :].squeeze(),
                               maxvalue=maxvalue)
        figure.add_subfigure(figname, caption=caption)
   
    return figure

def create_report_tensors(state, report_id):
    T = state.result.T
    vname = "" #TODO
    
    caption = '%s learned tensors, %d iterations' % \
        (vname, state.total_iterations)
    
    A = create_report_figure_tensors(T, same_scale=False, report_id='tensors',
        caption=caption)
    
    B = create_report_figure_tensors(T, same_scale=True, report_id='tensors-ss',
        caption='%s  (on the same scale)' % caption)
     
    return  ReportNode(id=report_id, nodeclass='tensor-father', children=[A, B])
 



    
