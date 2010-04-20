from re import match
from numpy import array
from pybv.simulation import load_state, save_state, is_state_available
from pybv_experiments.visualization import save_posneg_matrix


suite = 'dynamic_tensor'

jobs = ['firstorder_luminance_uniform_fields','firstorder_distance_uniform_fields']
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
            print "i = %s" % i
            print cmd_name
            f = field[:,:,i].squeeze()
            image_name ='%s-%s' % (field_name, cmd_name)
            save_posneg_matrix([suite, dirname, image_name ], f)

    