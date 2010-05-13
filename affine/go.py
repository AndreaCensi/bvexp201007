from numpy import floor, zeros, random

from compmake import comp, comp_prefix

from report_tools.node import ReportNode


from pybv.worlds import create_random_world, get_safe_pose
from pybv.simulation import random_motion_simulation 
from pybv_experiments import vehicles_list_A 
from pybv.sensors.textured_raytracer import TexturedRaytracer
from pybv_experiments.affine.affine import AffineModel, \
    create_report_affine

  
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

num_iterations = 500
dt = 0.1
 
vehicle_list = vehicles_list_A()
all_vehicle_report = []
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

    vehicle_report = comp(create_report_affine, state=result, report_id=vname)
    all_vehicle_report.append(vehicle_report)
comp_prefix()


def create_report(id, children):
    return ReportNode(id=id, children=children)

affine_report = comp(create_report, id='affine',
                          children=all_vehicle_report)
    
def write_report(report, filename):
    print report.children
    report.to_latex_document(filename)
    

comp(write_report, affine_report, "reports/affine.tex") 


