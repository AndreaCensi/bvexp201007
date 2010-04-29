from numpy import  random

from pybv.worlds import create_random_world, get_safe_pose
from pybv.sensors import TexturedRaytracer  
from pybv.simulation import random_motion_simulation, random_pose_simulation

from pybv_experiments import vehicles_list_A
from pybv_experiments.first_order.plot_parallel import plot_tensors, plot_covariance, \
    plot_tensors_tex
from pybv_experiments.first_order.normalize_tensor import normalize_tensor
from pybv_experiments.first_order.compute_fields import compute_fields, draw_fields, \
    draw_fields_tex
from pybv_experiments.covariance import SenselCovariance
from compmake import comp, comp_prefix



# FIXME: in this way, each time we create a different random world
world_radius = 10
world = create_random_world(radius=world_radius)

def my_world_gen():
    return create_random_world(radius=10)

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
    comp_prefix(vname)

    firstorder_result = comp(
        command=random_motion_simulation,
        world=world, vehicle=vehicle,
        random_pose_gen=random_pose_gen,
        num_iterations=num_iterations,
        random_commands_gen=random_commands_gen,
        processing_class=FirstorderSensels,
        job_id='first_order')

    plotting = comp(plot_tensors, state=firstorder_result,
         path=[vname, 'first_order'], prefix='normal_')
    comp(plot_tensors_tex, path=[vname, 'first_order'], prefix='normal_',
         label='%s-first_order' % vname, caption='?',
         extra_dep=plotting)

    covariance_result = comp(random_pose_simulation,
        world=world, vehicle=vehicle,
        random_pose_gen=random_pose_gen,
        num_iterations=num_iterations,
        processing_class=SenselCovariance)

    comp(plot_covariance, state=covariance_result,
         path=[vname, 'covariance'])
    
    normalization_result = comp(normalize_tensor, covariance_result, firstorder_result)

    plotting = comp(plot_tensors, state=normalization_result,
         path=[vname, 'first_order'], prefix='normalized_')
    comp(plot_tensors_tex, path=[vname, 'first_order'], prefix='normalized_',
         label='%s-first_order-normalized' % vname, caption='Result normalized',
         extra_dep=plotting)


    fields_result = comp(compute_fields, firstorder_result, world_gen=my_world_gen)
    fields_plot = comp(draw_fields, fields_result, path=[vname, 'first_order'],
                       prefix='normal_')
    comp(draw_fields_tex, path=[vname, 'first_order'], prefix='normal_',
         extra_dep=fields_plot)
    nfields_result = comp(compute_fields, normalization_result)
    nfields_plot = comp(draw_fields, fields_result, path=[vname, 'first_order'],
                        prefix='normalized_')
    comp(draw_fields_tex, path=[vname, 'first_order'], prefix='normalized_',
         extra_dep=nfields_plot)
    
if True:
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
