from numpy import linspace, deg2rad, isnan, array, dot
from pybv.utils import OpenStruct, RigidBodyState
from pybv.worlds import get_safe_pose
from pybv.sensors import TexturedRaytracer

from pybv_experiments.visualization import save_posneg_matrix
import numpy
from pybv.utils.numpy_utils import assert_reasonable_value, gt, require_shape
import math
from numpy.core.numeric import sign
from pybv_experiments.visualization.saving import save_probability_matrix, \
    save_success_matrix
from reprep.node import Node



def compute_command_fields(vehicle, T, reference_pose, vehicle_poses):
    """
     vehicle_poses: list of lists of Poses
     
     returns: list of list of command arrays
    """
    reference_data = vehicle.compute_observations(reference_pose)
    goal = reference_data.sensels 
    assert_reasonable_value(goal)
        
    results = []
    for row in vehicle_poses:
        results_row = []
        for pose_diff in row:
            pose = reference_pose.oplus(pose_diff)
            data = vehicle.compute_observations(pose)
            y = data.sensels
            assert_reasonable_value(y)
            commands = dot(dot(T, y), (goal - y)) 
            assert(len(commands) == vehicle.config.num_commands)
            results_row.append(commands)
            
        results.append(results_row) 
    return array(results)
    
    

def compute_fields(firstorder_result, world_gen, spacing_xy=1, spacing_theta=90,
                   resolution=15, previous_result=None):
    vehicle = firstorder_result.vehicle
    T = firstorder_result.result.T
    
    if previous_result is None:
        # Create the lattice for sampling
        lattice_x = linspace(-spacing_xy, spacing_xy, resolution)
        lattice_y = linspace(-spacing_xy, spacing_xy, resolution)
        lattice_theta = linspace(-deg2rad(spacing_theta),
                                 deg2rad(spacing_theta),
                                 resolution)
        
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
                get_safe_pose(raytracer, world_radius=7, # TODO: bounding box
                              safe_zone=1, num_tries=1000))
        del raytracer
    ref_pose = result.ref_poses[-1]
        
    vehicle.set_map(world)
    
    num = number_completed * 3
    total = (number_completed + 1) * 3
    
    yield (result, num, total) 
    if len(result.fields_x_y) <= number_completed:
        result.fields_x_y.append(
          compute_command_fields(vehicle, T, ref_pose, result.lattice_x_y))
    
    num += 1
    yield (result, num, total)
    if len(result.fields_x_theta) <= number_completed:
        result.fields_x_theta.append(
          compute_command_fields(vehicle, T, ref_pose, result.lattice_x_theta))
    num += 1
    yield (result, num, total)
    if len(result.fields_theta_y) <= number_completed:
        result.fields_theta_y.append(
          compute_command_fields(vehicle, T, ref_pose, result.lattice_theta_y))
    num += 1
    yield (result, num, total)

def create_report_fields(result, report_id=None):
    report = Node(report_id)
    
    fields = [('x_y', result.lattice_x_y, result.fields_x_y),
              ('x_theta', result.lattice_x_theta, result.fields_x_theta),
              ('theta_y', result.lattice_theta_y, result.fields_theta_y) ]

    fig_fields = report.figure('fields', caption='Inner products', shape=(3, 3))
    # Compute inner product w/ right direction
    fig_inner = report.figure(id='inner', caption='Inner products')

    fig_success = report.figure(id='success', caption='Success')
 
    
    for field_name, lattice, field in fields:
        field = array(field)
        average = numpy.mean(field, 0)
        #print "List  shape: %s " % str(field.shape)
        #print "Mean shape: %s " % str(average.shape)
        require_shape((gt(0), gt(0), 3), average)

        for i, cmd_name in [(0, 'vx'), (1, 'vy'), (2, 'vtheta')]:
            image_name = '%s-%s' % (field_name, cmd_name)

            fi = average[:, :, i].squeeze()
            require_shape((gt(0), gt(0)), fi)
            
            max_value = abs(fi).max()
            # let's allow a matrix with all 0
            if max_value == 0:
                max_value = 1

            report.data(image_name, fi)
            fig_fields.sub(image_name, display='posneg', max_value=max_value,
                           caption=field_name)
    
    def lattice2pose(lattice):
        def rbs2pose(rbs):
            p = rbs.get_2d_position()
            theta = rbs.get_2d_orientation()
            return array([p[0, 0], p[1, 0], theta])
        return map(lambda x: map(rbs2pose, x), lattice)
        
    for field_name, lattice, field in fields:
        lattice = array(lattice2pose(lattice))
        inners = []
        for commands in field:
            print "lattice shape", lattice.shape
            #print "commands shape", commands.shape
            inner = numpy.sum(lattice * commands, axis=2) 
            inners.append(inner)
        
        average_inner = numpy.mean(array(inners), 0)
        require_shape((gt(0), gt(0)), average_inner)
        
        success = numpy.mean(array(inners) > 0, 0) # XXX should be < 0
        require_shape((gt(0), gt(0)), success)
            
        image_name = 'inner-%s' % (field_name)
        
        max_value = abs(fi).max()
        # let's allow a matrix with all 0
        if max_value == 0:
            max_value = 1
        
        report.data(image_name, average_inner)
        fig_inner.sub(image_name, display='posneg',
                      max_value=max_value, caption=field_name)


        image_name = 'success-%s' % (field_name)
        
        report.data(image_name, success)
        fig_success.sub(image_name, display='success')


    return report

     
