''' These are some miscellaneous utils used by go_parallel '''
from pybv.worlds.world_generation import create_random_world
from pybv.sensors.textured_raytracer import TexturedRaytracer
from numpy import random
from reprep.out.html import node_to_html_document
from pybv.worlds.world_utils import get_safe_pose
from reprep.node import Node

def my_world_gen():
    return create_random_world(radius=10, num_lines=10, num_circles=10)

class MyPoseGen2:
    def set_map(self, world):
        self.raytracer = TexturedRaytracer()
        self.raytracer.set_map(world)
        
    def generate_pose(self):
        return get_safe_pose(
                             raytracer=self.raytracer,
                             world_radius=9,
                             safe_zone=0.5, num_tries=1000)
    def __eq__(self, other):
        ''' Without parameters, they will always compare true ''' 
        return True 

# Generate commands uniformly between -1,1
def my_random_commands_gen(ninteration, vehicle): #@UnusedVariable
    return  (random.rand(3) - 0.5) * 2

def create_report(id, children):
    print children
    return Node(id=id, children=children)
    
def write_report(report, basename):
    node_to_html_document(report, basename + '.html')
    
    