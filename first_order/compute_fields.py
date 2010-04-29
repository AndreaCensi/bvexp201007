from numpy import linspace, deg2rad, isnan, array, dot

from pybv import BVException
from pybv.utils import OpenStruct, RigidBodyState
from pybv.worlds import get_safe_pose
from pybv.sensors import TexturedRaytracer

from pybv_experiments.visualization import save_posneg_matrix
import numpy


def compute_command_fields(vehicle, T, reference_pose, vehicle_poses):
    """
     vehicle_poses: list of lists of Poses
     
     returns: list of list of command arrays
    """
    reference_data = vehicle.compute_observations(reference_pose)
    g = reference_data.sensels
    # FIXME: unused world???       
    results = []
    for row in vehicle_poses:
        results_row = []
        for pose_diff in row:
            pose = reference_pose.oplus(pose_diff)
            data = vehicle.compute_observations(pose)
            y = data.sensels
            if isnan(y).any():
                raise BVException('Found NaN in sensels')
            commands = dot(dot(T, y), (g - y)) 
            assert(len(commands) == vehicle.config.num_commands)
            results_row.append(commands)
            
            #sys.stderr.write('.')
        results.append(results_row)
        #sys.stderr.write('\n')
    #sys.stderr.write('\n\n')
    return array(results)
    

def compute_fields(firstorder_result, world_gen, spacing_xy=1, spacing_theta=90,
                   resolution=15, previous_result=None):
    vehicle = firstorder_result.vehicle
    T = firstorder_result.result.T
    
    if previous_result is None:
        # Create the lattice for sampling
        lattice_x = linspace(-spacing_xy, spacing_xy, resolution)
        lattice_y = linspace(-spacing_xy, spacing_xy, resolution)
        lattice_theta = linspace(-deg2rad(spacing_theta), deg2rad(spacing_theta), resolution)
        
        def make_grid(lattice_row, lattice_col, func):
            rows = []
            for y in lattice_row:
                row = []
                for x in lattice_col:
                    row.append(func(x, y))
                rows.append(row)
            return rows
         
        result = OpenStruct()
        result.lattice_x_y = make_grid(lattice_y, lattice_x,
                lambda y, x: RigidBodyState(position=[x, y]))
        result.lattice_x_theta = make_grid(lattice_theta, lattice_x,
                lambda theta, x: RigidBodyState(position=[x, 0], attitude=theta))
        result.lattice_theta_y = make_grid(lattice_y, lattice_theta,
                lambda y, theta: RigidBodyState(position=[0, y], attitude=theta))
        result.fields_x_y = []
        result.fields_x_theta = []
        result.fields_theta_y = []
        result.worlds = []
        result.ref_poses = []
    else:
        result = previous_result
    
    # This is the number of completed iterations
    number_completed = min([ len(x) \
        for x in [result.fields_x_y, result.fields_x_theta, result.fields_theta_y]])
    
    print "So far completed %s" % number_completed
    
    # sample world if we don't have one
    if len(result.worlds) <= number_completed:
        result.worlds.append(world_gen())
    world = result.worlds[-1]
    
    # sample pose if we don't have one   
    if len(result.ref_poses) <= number_completed:
        # Initalize raytracer for pose queries
        raytracer = TexturedRaytracer()
        raytracer.set_map(world)
        result.ref_poses.append(
                get_safe_pose(raytracer, world_radius=8, safe_zone=2)) # TODO: bounding box
        del raytracer
    ref_pose = result.ref_poses[-1]
        
    vehicle.set_map(world)
    
    yield (result, 0, 3) 
    if len(result.fields_x_y) <= number_completed:
        result.fields_x_y.append(compute_command_fields(vehicle, T,
                                              ref_pose, result.lattice_x_y))
    yield (result, 1, 3)
    if len(result.fields_x_theta) <= number_completed:
        result.fields_x_theta.append(compute_command_fields(vehicle, T,
                                                  ref_pose, result.lattice_x_theta))
    yield (result, 2, 3)
    if len(result.fields_theta_y) <= number_completed:
        result.fields_theta_y.append(compute_command_fields(vehicle, T,
                                                  ref_pose, result.lattice_theta_y))
    yield (result, 3, 3)

def draw_fields(result, path, prefix=''):
    fields = [('x_y', result.fields_x_y),
              ('x_theta', result.fields_x_theta),
              ('theta_y', result.fields_theta_y) ]

    for field_name, field in fields:
        field = array(field)
        average = numpy.mean(field, 0)
        print "List  shape: %s " % str(field.shape)
        print "Mean shape: %s " % str(average.shape)
        assert(len(average.shape) == 3)
        for i, cmd_name in [(0, 'vx'), (1, 'vy'), (2, 'vtheta')]:
            image_name = '%s-%s' % (field_name, cmd_name)
            impath = path + [ prefix + image_name ]
            
            f = average[:, :, i].squeeze()

            save_posneg_matrix(impath, f) 

def draw_fields_tex(path, prefix=''):
    # TODO
    pass
     
