from numpy import floor, zeros, random


from pybv.worlds import create_random_world, get_safe_pose
from pybv.simulation import random_motion_simulation 
from pybv_experiments import vehicles_list_A 
from compmake import comp, comp_prefix


from pybv.sensors.textured_raytracer import TexturedRaytracer
from pybv_experiments.visualization.saving import get_filename 
from pybv_experiments.affine.affine import affine_plot, AffineModel
  
def my_world_gen():
    return create_random_world(radius=10)

class MyPoseGen:
    
    def set_map(self, world):
        self.raytracer = TexturedRaytracer()
        self.raytracer.set_map(world)
        
    def generate_pose(self):
        pose = get_safe_pose(
                             raytracer=self.raytracer,
                             world_radius=9,
                             safe_zone=1, num_tries=100)
        #print "Found pose %s" % pose
        return pose

random_pose_gen = MyPoseGen() 

# Generate commands uniformly between -1,1
def my_random_commands_gen(ninteration, vehicle): #@UnusedVariable
    return  (random.rand(3) - 0.5) * 2

def my_random_commands_gen_special(ninteration, vehicle): #@UnusedVariable
    val = (random.rand(1) - 0.5) * 2
    i = int(floor(random.rand(1) * 2.99))
    u = zeros(3)
    u[i] = val
    return u

random_commands_gen = my_random_commands_gen

num_iterations = 100
dt = 0.5
 
vehicle_list = vehicles_list_A()

for vname, vehicle in vehicle_list:
    vname_tex = vname.replace('_', '-')
    comp_prefix(vname)

    result = comp(random_motion_simulation,
        world_gen=my_world_gen, vehicle=vehicle,
        random_pose_gen=random_pose_gen,
        num_iterations=num_iterations,
        random_commands_gen=random_commands_gen, dt=dt,
        processing_class=AffineModel,
        job_id='affine')


    plotting = comp(affine_plot, state=result,
         path=[vname], prefix='affine_')
comp_prefix('')


def write_index():
    fn = get_filename(['affine'], 'tex')
    print "Writing %s" % fn 
    f = open(fn, 'w')
    for vname, vehicle in vehicle_list:
        texname = vname.replace('_', '-')
        #vname = vname.replace('_','\\_')
        f.write("""
        
        \\cleardoublepage
        \\subsection{vdesc}
        
        \\subimport{vname/}{affine_index.tex}
        
        """.replace('vname', vname).replace('vdesc', texname))
        
    f.close()
    
    
comp(write_index)

