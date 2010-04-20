from sys import exit
from re import match

from numpy import array, ones

from pybv import BVException
from pybv.simulation import load_state, save_state, is_state_available
from pybv_experiments.visualization import save_posneg_matrix

failed = False
suite = 'dynamic_tensor'

jobs = ['firstorder_luminance_uniform_fields',
        'firstorder_distance_uniform_fields',
        'firstorder_polarized_fields',
        'firstorder_olfaction_fields']
for job in jobs:
    m = match('\A([A-Za-z]+)_(\w+)_[A-Za-z]+\Z', job)
    assert(m)
    vehicle_name = m.group(2)
    dirname = "firstorder_" + vehicle_name

    state = load_state(job)
    
    fields = [('x_y', state.field_x_y), 
              ('x_theta',state.field_x_theta), 
              ('theta_y', state.field_theta_y) ]

    for field_name, field in fields:
        field = array(field)
        assert(len(field.shape)==3)
        for i, cmd_name in [(0,'vx'),(1,'vy'),(2,'vtheta')]:
            f = field[:,:,i].squeeze()
            image_name ='%s-%s' % (field_name, cmd_name)
            path = [suite, dirname, image_name ]

            # TODO: add timestamp check
            try:
                save_posneg_matrix(path, f)
            except ValueError:
                print "could not draw %s" % path
                save_posneg_matrix(path, ones(shape=f.shape) ) 
                failed = True

if failed:
    exit(-1)