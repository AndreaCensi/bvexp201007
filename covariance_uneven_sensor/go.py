from pybv.worlds import create_random_world, get_safe_pose
from pybv.sensors import ImageRangeSensor
from pybv.utils import RigidBodyState
from pybv.simulation import random_pose_simulator
from numpy import deg2rad, linspace, pi, random
from numpy.linalg import norm
import sys
from Vehicle import * 

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
from luminance_covariance import LuminanceCovariance
result_luminance = random_pose_simulator(job_id='luminance_covariance', world=world, vehicle=vehicle, radius=world_radius, processing_class=LuminanceCovariance)

# second try: only ranges
vehicle2 = Vehicle()
vehicle2.add_rangefinder(sensor)
from readings_covariance import ReadingsCovariance
result_readings = random_pose_simulator(job_id='readings_covariance', world=world, vehicle=vehicle2, radius=world_radius, processing_class=ReadingsCovariance)

# third try: both ranges and luminance
vehicle3 = Vehicle()
vehicle3.add_optic_sensor(sensor)
vehicle3.add_rangefinder(sensor)

from sensel_covariance import SenselCovariance
result_sensels = random_pose_simulator(job_id='sensel_covariance', world=world, vehicle=vehicle3, radius=world_radius, processing_class=SenselCovariance)


from pybv.visualization import plot_covariance
from pylab import *
figure()
plot_covariance(result_sensels.cov_sensels)
figure()
plot_covariance(result_luminance.cov_luminance, sensor.directions)
figure()
plot_covariance(result_readings.cov_readings, sensor.directions)


