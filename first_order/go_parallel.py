from numpy import  random

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
from pybv_experiments.visualization.saving import get_filename
from pybv_experiments.covariance.first_order_sensels_normalize import  \
    FirstorderSenselsNormalizeUnif
 
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
                             safe_zone=0.5, num_tries=200)

random_pose_gen = MyPoseGen() 

# Generate commands uniformly between -1,1
def my_random_commands_gen(ninteration, vehicle): #@UnusedVariable
    return  (random.rand(3) - 0.5) * 2

random_commands_gen = my_random_commands_gen

num_iterations = 500
dt = 0.5
 
vehicle_list = vehicles_list_A()

for vname, vehicle in vehicle_list:
    vname_tex = vname.replace('_', '-')
    comp_prefix(vname)

    firstorder_result = comp(
        command=random_motion_simulation,
        world_gen=my_world_gen, vehicle=vehicle,
        random_pose_gen=random_pose_gen,
        num_iterations=num_iterations,
        random_commands_gen=random_commands_gen, dt=dt,
        processing_class=FirstorderSenselsNormalizeUnif,
        job_id='first_order')

    plotting = comp(plot_tensors, state=firstorder_result,
         path=[vname], prefix='natural_')
    comp(plot_tensors_tex, path=[vname], prefix='natural_',
         figure_label='%s-first_order' % vname_tex,
         figure_caption='%s-natural' % vname_tex,
         extra_dep=plotting)

    covariance_result = comp(random_pose_simulation,
        world_gen=my_world_gen, vehicle=vehicle,
        random_pose_gen=random_pose_gen,
        num_iterations=num_iterations,
        processing_class=SenselCovariance)

    comp(plot_covariance, state=covariance_result,
         path=[vname])
    comp(plot_covariance_tex, path=[vname],
         figure_caption='%s correlation' % vname_tex)
    
    normalization_result = comp(normalize_tensor, covariance_result, firstorder_result)

    plotting = comp(plot_tensors, state=normalization_result,
         path=[vname], prefix='normalized_')
    comp(plot_tensors_tex, path=[vname], prefix='normalized_',
         figure_label='%s-first_order-normalized' % vname_tex,
         figure_caption='%s-normalized' % vname_tex,
         extra_dep=plotting)


    fields_result = comp(compute_fields, firstorder_result, world_gen=my_world_gen,
                         job_id='fields')
    fields_plot = comp(draw_fields, fields_result, path=[vname],
                       prefix='natural_')
    comp(draw_fields_tex, path=[vname], prefix='natural_',
         figure_caption='%s-natural fields' % vname_tex,
         extra_dep=fields_plot)
    nfields_result = comp(compute_fields, normalization_result, world_gen=my_world_gen,
                          job_id='nfields')
    nfields_plot = comp(draw_fields, nfields_result, path=[vname],
                        prefix='normalized_')
    comp(draw_fields_tex, path=[vname], prefix='normalized_',
        figure_caption='%s-normalized fields' % vname_tex,
         extra_dep=nfields_plot)
    
if True:
    fn = get_filename(['all_vehicles'], 'tex')
    print "Writing %s" % fn 
    f = open(fn, 'w')
    for vname, vehicle in vehicle_list:
        
        texname = vname.replace('_', '-')
        #vname = vname.replace('_','\\_')
        f.write("""
        
        \\cleardoublepage
        \\subsection{vdesc}
        
        \\subimport{vname/}{covariance.tex}
        \\subimport{vname/}{natural_tensors.tex}
        \\subimport{vname/}{natural_fields.tex}
        \\subimport{vname/}{normalized_tensors.tex}
        \\subimport{vname/}{normalized_fields.tex}
        
        """.replace('vname', vname).replace('vdesc', texname))
        
    f.close()
