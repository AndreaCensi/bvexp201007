from numpy import  random

from pybv.worlds import create_random_world, get_safe_pose
from pybv.sensors import TexturedRaytracer  
from pybv.simulation import random_motion_simulation, random_pose_simulation

from pybv_experiments import vehicles_list_A
from pybv_experiments.first_order.plot_parallel import plot_tensors, plot_covariance
from pybv_experiments.first_order.normalize_tensor import normalize_tensor
from pybv_experiments.first_order.compute_fields import compute_fields, draw_fields
from compmake import add_computation
from pybv_experiments.covariance import SenselCovariance

# FIXME: in this way, each time we create a different random world
world_radius = 10
world = create_random_world(radius=world_radius)

from pybv_experiments.first_order import  FirstorderSensels

raytracer = TexturedRaytracer()
raytracer.set_map(world)

def my_random_pose_gen(niteration): #@UnusedVariable
    return get_safe_pose(
        raytracer=raytracer, world_radius=0.9 * world_radius,
        safe_zone=0.5, num_tries=100)
    
random_pose_gen = my_random_pose_gen 

# Generate commands uniformly between -1,1
def my_random_commands_gen(ninteration, vehicle): #@UnusedVariable
    return  (random.rand(3) - 0.5) * 2

random_commands_gen = my_random_commands_gen

num_iterations = 100
 
vehicle_list = vehicles_list_A()

for vname, vehicle in vehicle_list:
    first_order_job_id = '%s-first_order' % vname

    add_computation(depends=[], parsim_job_id=first_order_job_id,
                          command=random_motion_simulation,
        world=world, vehicle=vehicle,
        random_pose_gen=random_pose_gen,
        num_iterations=num_iterations,
        random_commands_gen=random_commands_gen,
        processing_class=FirstorderSensels)

    add_computation(depends=first_order_job_id,
                    parsim_job_id=first_order_job_id + '-plot_tensors',
                    command=plot_tensors,
                    conf_name=vname)

    covariance_job_id = '%s-covariance' % vname

    add_computation(depends=[], parsim_job_id=covariance_job_id,
                          command=random_pose_simulation,
        world=world, vehicle=vehicle,
        random_pose_gen=random_pose_gen,
        num_iterations=num_iterations,
        processing_class=SenselCovariance)

    add_computation(depends=covariance_job_id,
                    parsim_job_id=covariance_job_id + '-plot_tensors',
                    command=plot_covariance,
                    conf_name=vname)
    
    normalization_job_id = '%s-normalized' % vname
    
    add_computation(depends=[covariance_job_id, first_order_job_id],
                    parsim_job_id=normalization_job_id,
                    command=normalize_tensor)

    add_computation(depends=normalization_job_id,
                    parsim_job_id=normalization_job_id + '-plot_tensors',
                    command=plot_tensors,
                    conf_name=vname, prefix='normalized_')
    

    fields_job_id = '%s-fields' % vname
    add_computation(depends=first_order_job_id, parsim_job_id=fields_job_id,
                    command=compute_fields)
    
    draw_fields_job_id = '%s-draw_fields' % vname
    add_computation(depends=fields_job_id, parsim_job_id=draw_fields_job_id,
                    command=draw_fields, conf_name=vname)


f = open('../tex/all_vehicles.tex', 'w')
for vname, vehicle in vehicle_list:
    
    texname = vname.replace('_', '-')
    #vname = vname.replace('_','\\_')
    f.write("""
    
    \\cleardoublepage
    \\subsection{vdesc}
    
    \\showcovariances{vname}{vdesc}
    \\showtensors{vname}{vdesc}
    \\showgrids{vname}{vdesc}
    
    """.replace('vname', vname).replace('vdesc', texname))
    
f.close()
