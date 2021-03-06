import unittest
from pybv.sensors import Rangefinder, Optics
from pieces import vehicles_list_A, create_uniform_sensor, create_example_nonuniform
from pybv.utils.misc import make_sure_pickable

class Basics(unittest.TestCase):
    
    def testCorrectExecution(self):
        create_uniform_sensor(Rangefinder(), fov_deg=180, num_rays=180)
        create_example_nonuniform(Rangefinder())
        create_uniform_sensor(Optics(), fov_deg=180, num_rays=180)
        create_example_nonuniform(Optics())
    
    def testPickable(self):
        ''' Making sure that all test vehicles are pickable '''
        for name, vehicle in vehicles_list_A(): #@UnusedVariable
            v2 = make_sure_pickable(vehicle)
            make_sure_pickable(v2)
