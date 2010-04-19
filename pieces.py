""" Standard pieces used in the experiments """
from numpy import deg2rad, pi, linspace, array, cos, sin

from pybv.sensors import ImageRangeSensor, OlfactionSensor
from pybv.utils import RigidBodyState

def create_uniform_sensor(sensor, fov_deg, num_rays, spatial_sigma_deg=0.5, sigma=0.01):
    """ Creates a uniform image/range sensor whose rays are uniformly distributed """
    directions = deg2rad(linspace(-fov_deg/2,fov_deg/2, num_rays))
    sensor.add_photoreceptors(directions, spatial_sigma=deg2rad(spatial_sigma_deg), sigma=sigma)
    return sensor

def create_example_nonuniform(sensor):
    """ Design the following sensor:
        * acute frontal view   [-30deg : 1 : 30deg]  spatial_sigma=1
        * sparse side view   [-90 : 3 : -30]  U [30 : 3 : 90]  spatial_sigma=1
        * sparse & ??? backward  view   [-90 : 3 : -270]  spatial_sigma=3
    """
    sensor.add_photoreceptors(deg2rad(range(-30,30,1)), spatial_sigma=deg2rad(2), sigma=0.01)
    sensor.add_photoreceptors(deg2rad(range(-90,-30,3)), spatial_sigma=deg2rad(2), sigma=0.01)
    sensor.add_photoreceptors(deg2rad(range(+30,+90,3)), spatial_sigma=deg2rad(2), sigma=0.01)
    sensor.add_photoreceptors(deg2rad(range(-90,-270,3)), spatial_sigma=deg2rad(5), sigma=0.01)
    return sensor
    
def create_ring_olfaction_sensor(fov_deg, num_sensors, radius):
    """ Creates an olfaction sensor whose receptors are set in a ring"""
    of = OlfactionSensor()
    directions = deg2rad(linspace(-fov_deg/2,fov_deg/2, num_sensors))
    for theta in directions:
        position = array([cos(theta), sin(theta)]) * radius
        sensitivity = {'food': 1}
        of.add_receptor( pose=RigidBodyState(position=position), sensitivity=sensitivity)
    return of
    