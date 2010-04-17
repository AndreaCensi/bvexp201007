from pybv.worlds import create_random_world, get_safe_pose
from pybv.sensors import ImageRangeSensor, TexturedRaytracer
from pybv.utils import RigidBodyState, OpenStruct
from pybv.vehicle import Vehicle, OmnidirectionalKinematics
from pybv.simulation import random_motion_simulation
from pybv_experiments import create_uniform_sensor, create_example_nonuniform
from numpy import deg2rad, linspace, pi, random
from numpy.linalg import norm
import sys

world_radius = 10
world = create_random_world(radius=world_radius)

sensor_uniform = create_uniform_sensor(fov_deg=360, num_rays=180, spatial_sigma_deg=0.5, sigma=0.01)
sensor_uniform.set_map(world)

sensor_nonuniform = create_example_nonuniform()
sensor_nonuniform.set_map(world)

from dynamic_tensor import DynamicTensor
from firstorder_readings import *

raytracer = TexturedRaytracer()
raytracer.set_map(world)
random_pose_gen = lambda niteration: get_safe_pose(
        raytracer=raytracer, world_radius=0.9*world_radius, 
        safe_zone=0.5, num_tries=100)

random_commands_gen = lambda niteration, vehicle: random.rand(3)

num_iterations = 100

if 'many' in sys.argv:
    num_iterations = 100000

all_jobs = {}
sensors = {'uniform': sensor_uniform, 'nonuniform': sensor_nonuniform } 

for sensor_name, sensor in sensors.items():
    job_id = 'firstorder_luminance_%s' % sensor_name

    vehicle = Vehicle()
    vehicle.add_optic_sensor(sensor)
    vehicle.set_dynamics(OmnidirectionalKinematics())
    
    all_jobs[job_id] = random_motion_simulation(
        job_id=job_id,
        world=world, vehicle=vehicle,  
        random_pose_gen=random_pose_gen, 
        num_iterations=num_iterations, 
        random_commands_gen=random_commands_gen,     
        processing_class=DynamicTensor)

# now for rangefinder
for sensor_name, sensor in sensors.items():
    job_id = 'firstorder_distance_%s' % sensor_name

    vehicle = Vehicle()
    vehicle.add_rangefinder(sensor)
    vehicle.set_dynamics(OmnidirectionalKinematics())

    all_jobs[job_id] = random_motion_simulation(
        job_id=job_id,
        world=world, vehicle=vehicle,  
        random_pose_gen=random_pose_gen, 
        num_iterations=num_iterations, 
        random_commands_gen=random_commands_gen,     
        processing_class=FirstorderDistance)

all_jobs = OpenStruct(**all_jobs)
