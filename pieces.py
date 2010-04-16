""" Standard pieces """

from pybv.sensors import ImageRangeSensor
from numpy import deg2rad, pi, linspace

def create_uniform_sensor(fov_deg, num_rays, spatial_sigma_deg=0.5, sigma=0.01):
    sensor = ImageRangeSensor()
    sensor.add_photoreceptors(deg2rad(linspace(-fov_deg/2,fov_deg/2, num_rays)), spatial_sigma=deg2rad(spatial_sigma_deg), sigma=sigma)
    return sensor
    

def create_example_nonuniform():
    """ Design the following sensor:
        * acute frontal view   [-30deg : 1 : 30deg]  spatial_sigma=1
        * sparse side view   [-90 : 3 : -30]  U [30 : 3 : 90]  spatial_sigma=1
        * sparse & ??? backward  view   [-90 : 3 : -270]  spatial_sigma=3
    """
    sensor = ImageRangeSensor()
    sensor.add_photoreceptors(deg2rad(range(-30,30,1)), spatial_sigma=deg2rad(2), sigma=0.01)
    sensor.add_photoreceptors(deg2rad(range(-90,-30,3)), spatial_sigma=deg2rad(2), sigma=0.01)
    sensor.add_photoreceptors(deg2rad(range(+30,+90,3)), spatial_sigma=deg2rad(2), sigma=0.01)
    sensor.add_photoreceptors(deg2rad(range(-90,-270,3)), spatial_sigma=deg2rad(5), sigma=0.01)
    return sensor
    