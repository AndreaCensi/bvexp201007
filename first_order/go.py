import sys

from numpy import deg2rad, linspace, pi, random
from numpy.linalg import norm

from pybv.worlds import create_random_world, get_safe_pose
from pybv.sensors import ImageRangeSensor, TexturedRaytracer, OlfactionSensor, \
    Rangefinder, Optics, PolarizedLightSensor
from pybv.utils import RigidBodyState, OpenStruct
from pybv.vehicle import Vehicle, OmnidirectionalKinematics
from pybv.simulation import random_motion_simulation

from pybv_experiments import create_uniform_sensor, create_example_nonuniform, \
    create_ring_olfaction_sensor

world_radius = 10
world = create_random_world(radius=world_radius)

from pybv_experiments.first_order import \
    DynamicTensor, FirstorderDistance, FirstorderSensels

raytracer = TexturedRaytracer()
raytracer.set_map(world)
random_pose_gen = lambda niteration: get_safe_pose(
        raytracer=raytracer, world_radius=0.9*world_radius, 
        safe_zone=0.5, num_tries=100)

# TOTHINK: with this, Tx=Ty=Ttheta
# random_commands_gen = lambda niteration, vehicle: random.rand(3)

# Generate commands uniformly between -1,1
random_commands_gen = lambda niteration, vehicle: (random.rand(3)-0.5)*2

num_iterations = 100

if 'many' in sys.argv:
    num_iterations = 10000

all_jobs = {}
sensors_optics = {'uniform': create_uniform_sensor(Optics(), 
                        fov_deg=360, num_rays=180, 
                        spatial_sigma_deg=0.5, sigma=0.01), 
           'nonuniform': create_example_nonuniform(Optics()) } 

for sensor_name, sensor in sensors_optics.items():
    job_id = 'firstorder_luminance_%s' % sensor_name

    vehicle = Vehicle()
    vehicle.add_sensor(sensor)
    vehicle.set_dynamics(OmnidirectionalKinematics())
    
    all_jobs[job_id] = random_motion_simulation(
        job_id=job_id,
        world=world, vehicle=vehicle,  
        random_pose_gen=random_pose_gen, 
        num_iterations=num_iterations, 
        random_commands_gen=random_commands_gen,     
        processing_class=DynamicTensor)


sensors_rangefinder = {'uniform': create_uniform_sensor(Rangefinder(), 
                        fov_deg=360, num_rays=180, 
                        spatial_sigma_deg=0.5, sigma=0.01), 
           'nonuniform': create_example_nonuniform(Rangefinder()) } 

# now for rangefinder
for sensor_name, sensor in sensors_rangefinder.items():
    job_id = 'firstorder_distance_%s' % sensor_name

    vehicle = Vehicle()
    vehicle.add_sensor(sensor)
    vehicle.set_dynamics(OmnidirectionalKinematics())

    all_jobs[job_id] = random_motion_simulation(
        job_id=job_id,
        world=world, vehicle=vehicle,  
        random_pose_gen=random_pose_gen, 
        num_iterations=num_iterations, 
        random_commands_gen=random_commands_gen,     
        processing_class=FirstorderDistance)

# now for olfaction
if 1:
    job_id = 'firstorder_olfaction' 
    os = create_ring_olfaction_sensor(fov_deg=180, num_sensors=40, radius=0.3)
    vehicle = Vehicle()
    vehicle.add_sensor(os)
    vehicle.set_dynamics(OmnidirectionalKinematics())

    all_jobs[job_id] = random_motion_simulation(
        job_id=job_id,
        world=world, vehicle=vehicle,  
        random_pose_gen=random_pose_gen, 
        num_iterations=num_iterations, 
        random_commands_gen=random_commands_gen,     
        processing_class=FirstorderSensels)

# now for olfaction
if 1:
    job_id = 'firstorder_polarized' 
    vehicle = Vehicle()
    vehicle.add_sensor(PolarizedLightSensor(45))
    vehicle.set_dynamics(OmnidirectionalKinematics())

    all_jobs[job_id] = random_motion_simulation(
        job_id=job_id,
        world=world, vehicle=vehicle,  
        random_pose_gen=random_pose_gen, 
        num_iterations=num_iterations, 
        random_commands_gen=random_commands_gen,     
        processing_class=FirstorderSensels)

all_jobs = OpenStruct(**all_jobs)
