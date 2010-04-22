""" Standard pieces used in the experiments """
from numpy import deg2rad, pi, linspace, array, cos, sin

from pybv.sensors import *
from pybv.vehicle import Vehicle, OmnidirectionalKinematics
from pybv.utils import RigidBodyState, make_sure_pickable

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
    
    
def vehicles_list_A():
    """ 
    Returns a list of vehicles to compare. 
    
    Returns a list of tuples (name, vehicle) """
    
    vlist = []

    vehicle = Vehicle()
    vehicle.set_dynamics(OmnidirectionalKinematics())
    sensor = create_uniform_sensor(Optics(), 
                        fov_deg=360, num_rays=180, 
                        spatial_sigma_deg=0.5, sigma=0.01)
    vehicle.add_sensor(sensor)
    vlist.append(('v_optic_unif', vehicle))
    
    vehicle = Vehicle()
    vehicle.set_dynamics(OmnidirectionalKinematics())
    sensor = create_example_nonuniform(Optics())
    vehicle.add_sensor(sensor)
    vlist.append(('v_optic_nonunif', vehicle))
    
    vehicle = Vehicle()
    vehicle.set_dynamics(OmnidirectionalKinematics())
    sensor = create_uniform_sensor(Rangefinder(), 
                        fov_deg=360, num_rays=180, 
                        spatial_sigma_deg=0.5, sigma=0.01)
    vehicle.add_sensor(sensor)
    vlist.append(('v_rangefinder_unif', vehicle))

    vehicle = Vehicle()
    vehicle.set_dynamics(OmnidirectionalKinematics())
    sensor = create_example_nonuniform(Rangefinder())
    vehicle.add_sensor(sensor)
    vlist.append(('v_rangefinder_nonunif', vehicle))

    vehicle = Vehicle()
    vehicle.set_dynamics(OmnidirectionalKinematics())
    sensor = create_ring_olfaction_sensor(fov_deg=180, num_sensors=40, radius=0.3)
    vehicle.add_sensor(sensor)
    vlist.append(('v_olfaction', vehicle))

    vehicle = Vehicle()
    vehicle.set_dynamics(OmnidirectionalKinematics())
    vehicle.add_sensor(PolarizedLightSensor(45))
    vlist.append(('v_polarized', vehicle))

    return vlist
    
    
        
