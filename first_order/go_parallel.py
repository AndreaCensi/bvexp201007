from numpy import  random

from pybv_experiments.first_order import  FirstorderSensels
from pybv.worlds import create_random_world, get_safe_pose
from pybv.simulation import random_motion_simulation, random_pose_simulation

from pybv_experiments import vehicles_list_A
from pybv_experiments.first_order.plot_parallel import plot_tensors, plot_covariance, \
    plot_tensors_tex, plot_covariance_tex
from pybv_experiments.first_order.normalize_tensor import normalize_tensor
from pybv_experiments.first_order.compute_fields import compute_fields, draw_fields, \
    draw_fields_tex
from pybv_experiments.covariance import SenselCovariance
from compmake import comp, comp_prefix
from pybv.sensors.textured_raytracer import TexturedRaytracer
 
def my_world_gen():
    return create_random_world(radius=10)



class MyPoseGen:
    def set_map(self, world):
        self.raytracer = TexturedRaytracer()
        self.raytracer.set_map(world)
    def generate_pose(self):
        return get_safe_pose(
                             raytracer=self.raytracer,
                             world_radius=9,
                             safe_zone=0.5, num_tries=100)

random_pose_gen = MyPoseGen() 

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
        world_gen=my_world_gen, vehicle=vehicle,
        random_pose_gen=random_pose_gen,
        num_iterations=num_iterations,
        random_commands_gen=random_commands_gen,
        processing_class=FirstorderSensels,
        job_id='first_order')

    plotting = comp(plot_tensors, state=firstorder_result,
         path=[vname, 'first_order'], prefix='natural_')
    comp(plot_tensors_tex, path=[vname, 'first_order'], prefix='natural_',
         label='%s-first_order' % vname, caption='?',
         extra_dep=plotting)

    covariance_result = comp(random_pose_simulation,
        world_gen=my_world_gen, vehicle=vehicle,
        random_pose_gen=random_pose_gen,
        num_iterations=num_iterations,
        processing_class=SenselCovariance)

    comp(plot_covariance, state=covariance_result,
         path=[vname, 'covariance'])
    comp(plot_covariance_tex, path=[vname, 'covariance'])
    
    normalization_result = comp(normalize_tensor, covariance_result, firstorder_result)

    plotting = comp(plot_tensors, state=normalization_result,
         path=[vname, 'first_order'], prefix='normalized_')
    comp(plot_tensors_tex, path=[vname, 'first_order'], prefix='normalized_',
         label='%s-first_order-normalized' % vname, caption='Result normalized',
         extra_dep=plotting)


    fields_result = comp(compute_fields, firstorder_result, world_gen=my_world_gen,
                         job_id='fields')
    fields_plot = comp(draw_fields, fields_result, path=[vname, 'first_order'],
                       prefix='natural_')
    comp(draw_fields_tex, path=[vname, 'first_order'], prefix='natural_',
         extra_dep=fields_plot)
    nfields_result = comp(compute_fields, normalization_result, world_gen=my_world_gen,
                          job_id='nfields')
    nfields_plot = comp(draw_fields, nfields_result, path=[vname, 'first_order'],
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
