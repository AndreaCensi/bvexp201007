from pybv.worlds import create_random_world, get_safe_pose
from pybv.sensors import ImageRangeSensor, TexturedRaytracer
from pybv.utils import RigidBodyState
from pybv.vehicle import Vehicle, OmnidirectionalKinematics
from pybv.simulation import random_motion_simulation
from numpy import deg2rad, linspace, pi, random
from numpy.linalg import norm
import sys

world_radius = 10
world = create_random_world(radius=world_radius)

# design the following sensor:
# acute frontal view   [-30deg : 1 : 30deg]  spatial_sigma=1
# sparse side view   [-90 : 3 : -30]  U [30 : 3 : 90]  spatial_sigma=1
# sparse & ??? backward  view   [-90 : 3 : -270]  spatial_sigma=3
sensor = ImageRangeSensor(world=world)
sensor.add_photoreceptors(deg2rad(range(-30,30,1)), spatial_sigma=deg2rad(2), sigma=0.01)
sensor.add_photoreceptors(deg2rad(range(-90,-30,3)), spatial_sigma=deg2rad(2), sigma=0.01)
sensor.add_photoreceptors(deg2rad(range(+30,+90,3)), spatial_sigma=deg2rad(2), sigma=0.01)
sensor.add_photoreceptors(deg2rad(range(-90,-270,3)), spatial_sigma=deg2rad(5), sigma=0.01)

# first try: only luminance
vehicle = Vehicle()
vehicle.add_optic_sensor(sensor)
vehicle.set_dynamics(OmnidirectionalKinematics())

from dynamic_tensor import DynamicTensor

raytracer = TexturedRaytracer()
raytracer.set_map(world)
random_pose_gen = lambda niteration: get_safe_pose(
        raytracer=raytracer, world_radius=world_radius, 
        safe_zone=0.5, num_tries=100)

random_commands_gen = lambda niteration, vehicle: random.rand(3)

result = random_motion_simulation(job_id='dynamic_tensor', world=world, vehicle=vehicle,  random_pose_gen=random_pose_gen, random_commands_gen=random_commands_gen,     processing_class=DynamicTensor)

