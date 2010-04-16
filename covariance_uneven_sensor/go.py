from pybv.worlds import create_random_world, get_safe_pose
from pybv.sensors import ImageRangeSensor, TexturedRaytracer
from pybv.utils import RigidBodyState
from pybv.vehicle import Vehicle
from pybv.simulation import random_pose_simulation
from pybv_experiments import create_uniform_sensor, create_example_nonuniform
from numpy import deg2rad, pi, random
from numpy.linalg import norm
import sys

world_radius = 10
world = create_random_world(radius=world_radius)

sensor_uniform = create_uniform_sensor(fov_deg=360, num_rays=180, spatial_sigma_deg=0.5, sigma=0.01)
sensor_uniform.set_map(world)

sensor_nonuniform = create_example_nonuniform()
sensor_nonuniform.set_map(world)

# Pose generation uses a raytracer to find good poses
raytracer = TexturedRaytracer()
raytracer.set_map(world)
random_pose_gen = lambda niteration: get_safe_pose(
        raytracer=raytracer, world_radius=0.9*world_radius, 
        safe_zone=0.5, num_tries=100)

num_iterations = 100

from luminance_covariance import LuminanceCovariance
from readings_covariance import ReadingsCovariance
from sensel_covariance import SenselCovariance

sensors = {'uniform': sensor_uniform, 'nonuniform': sensor_nonuniform } 

for sensor_name, sensor in sensors.items():
    job_id = 'covariance_luminance_%s' % sensor_name

    # first try: only luminance
    vehicle = Vehicle()
    vehicle.add_optic_sensor(sensor)
    
    random_pose_simulation(job_id=job_id, world=world, vehicle=vehicle, random_pose_gen=random_pose_gen, num_iterations=num_iterations, processing_class=LuminanceCovariance) 

    # second try: only ranges
    vehicle2 = Vehicle()
    vehicle2.add_rangefinder(sensor)
    job_id = 'covariance_distance_%s' % sensor_name
    random_pose_simulation(job_id=job_id, world=world, vehicle=vehicle2, random_pose_gen=random_pose_gen, num_iterations=num_iterations, processing_class=ReadingsCovariance)

    # third try: both ranges and luminance
    vehicle3 = Vehicle()
    vehicle3.add_optic_sensor(sensor)
    vehicle3.add_rangefinder(sensor)

    job_id = 'covariance_sensels_%s' % sensor_name
    random_pose_simulation(job_id=job_id, world=world, vehicle=vehicle3,  random_pose_gen=random_pose_gen, num_iterations=num_iterations, processing_class=SenselCovariance)

