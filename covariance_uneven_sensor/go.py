from pybv.worlds import create_random_world, get_safe_pose
from pybv.sensors import ImageRangeSensor
from pybv.utils import RigidBodyState
from numpy import deg2rad, linspace, pi, random
from numpy.linalg import norm
import sys
from Vehicle import * 

world_radius = 10
world = create_random_world(radius=world_radius)

sensor = ImageRangeSensor(world=world)
sensor.add_photoreceptors(linspace(-pi/2, pi/2, 100), spatial_sigma=deg2rad(5), sigma=0.01)
sensor.add_photoreceptors(linspace(-pi/6, pi/6,  20), spatial_sigma=deg2rad(2), sigma=0.01)

vehicle = Vehicle()
vehicle.add_optic_sensor(sensor)
vehicle.set_dynamics(OmnidirectionalKinematics())
vehicle.set_controller(None)

from luminance_covariance import LuminanceCovariance
ac = LuminanceCovariance(vehicle.config)

for i in range(1000):
    state = get_safe_pose(raytracer=sensor, world_radius=world_radius, safe_zone=0.5, num_tries=100)
    vehicle.set_state(state)
    data = vehicle.compute_observations()
    ac.process_data(data)
    sys.stderr.write('.')
    
print answer





