import sys
import time

from numpy import linspace, deg2rad, isnan, array

from pybv import BVException
from pybv.utils import OpenStruct, RigidBodyState
from pybv.simulation import load_state, save_state, is_state_available
from pybv.worlds import create_random_world, get_safe_pose
from pybv.sensors import TexturedRaytracer

from pybv_experiments.visualization import *
from dynamic_tensor import *

def compute_command_fields(world, vehicle, T, reference_pose, vehicle_poses):
    """
     vehicle_poses: list of lists of Poses
     
     returns: list of list of command arrays
    """
    reference_data = vehicle.compute_observations(reference_pose)
    g = reference_data.sensels
            
    results = []
    for row in vehicle_poses:
        results_row = []
        for pose_diff in row:
            pose = reference_pose.oplus(pose_diff)
            data = vehicle.compute_observations(pose)
            y = data.sensels
            if isnan(y).any():
                raise BVException('Found NaN in sensels')
            commands =  dot(dot(T, y), (g - y)) 
            assert(len(commands) == vehicle.config.num_commands)
            results_row.append(commands)
            
            sys.stderr.write('.')
        results.append(results_row)
        sys.stderr.write('\n')
    sys.stderr.write('\n\n')
    return results
    

def compute_fields(state):
    vehicle = state.vehicle
    world = state.world
    T = state.result.T
    raytracer = TexturedRaytracer()
    raytracer.set_map(world)
    ref_pose = get_safe_pose(raytracer, world_radius=8, safe_zone=2) # TODO: bounding box
    
    # Create the lattice for sampling
    resolution = 20
    lattice_x = linspace(-1, 1, resolution)
    lattice_y = linspace(-1, 1, resolution)
    lattice_theta = linspace(-deg2rad(90), deg2rad(90), resolution)
    
    def make_grid(lattice_row, lattice_col, func):
        rows = []
        for y in lattice_row:
            row = []
            for x in lattice_col:
                row.append(func(x,y))
            rows.append(row)
        return rows
    
    lattice_x_y = make_grid(lattice_y, lattice_x, 
            lambda y, x: RigidBodyState(position=[x,y]) )
    
    lattice_x_theta = make_grid(lattice_theta, lattice_x, 
            lambda theta, x: RigidBodyState(position=[x,0], attitude=theta) )
    
    lattice_theta_y = make_grid(lattice_y, lattice_theta, 
            lambda y, theta: RigidBodyState(position=[0,y], attitude=theta) )
    

    result = OpenStruct()
    result.lattice_x_y = lattice_x_y
    result.field_x_y = compute_command_fields(world, vehicle, T, 
                                              ref_pose, lattice_x_y)
    result.lattice_x_theta = lattice_x_theta
    result.field_x_theta = compute_command_fields(world, vehicle, T, 
                                                  ref_pose, lattice_x_theta)
    result.lattice_theta_y = lattice_theta_y
    result.field_theta_y = compute_command_fields(world, vehicle, T,  
                                                  ref_pose, lattice_theta_y)
    result.timestamp = time.time()

    return result


def draw_fields(result, conf_name):
    suite = 'fields'
    
    fields = [('x_y', result.field_x_y), 
              ('x_theta',result.field_x_theta), 
              ('theta_y', result.field_theta_y) ]

    for field_name, field in fields:
        field = array(field)
        assert(len(field.shape)==3)
        for i, cmd_name in [(0,'vx'),(1,'vy'),(2,'vtheta')]:
            image_name ='%s-%s' % (field_name, cmd_name)
            path = [conf_name, suite, image_name ]
            
            f = field[:,:,i].squeeze()
#            try:
            save_posneg_matrix(path, f)
 #           except ValueError as e:
  #              print "could not draw %s: %s" % (path, e)
   #             save_posneg_matrix(path, ones(shape=f.shape) ) 
    #            failed = True
                