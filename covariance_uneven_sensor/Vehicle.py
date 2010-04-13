from pybv.utils import OpenStruct, RigidBodyState

class Command:
    def __init__(self, id, desc, min, max, rest):
        self.id = id
        self.desc = desc
        self.min = min
        self.max = max
        self.rest = rest
             
class Dynamics:
    def __init__(self):
        self.commands = []
    def add_command(self, command):
        self.commands.append(command)
    
class OmnidirectionalKinematics(Dynamics):
    def __init__(self):
        Dynamics.__init__(self)
        self.add_command(Command(id='vx',desc='linear velocity (x)', min=-0.5, max=+0.5, rest=0))
        self.add_command(Command(id='vy',desc='linear velocity (y)', min=-0.5, max=+0.5, rest=0))
        self.add_command(Command(id='vtheta',desc='angular velocity', min=-1, max=+1, rest=0))

class Vehicle:
    def __init__(self):
        self.config = OpenStruct()
        self.config.optics = []
        self.config.rangefinder = []
        self.config.num_sensels = 0 
        
        self.config.dynamics = None
        self.state = RigidBodyState()
        
    def add_optic_sensor(self, sensor, mountpoint=RigidBodyState()):
        # FIXME add mountpoint 
        self.config.optics.append(sensor)
        self.config.num_sensels += sensor.num_photoreceptors
    
    def add_rangefinder(self, sensor, mountpoint=RigidBodyState()):
        # FIXME add mountpoint 
        self.config.rangefinder.append(sensor)
        self.config.num_sensels += sensor.num_readings
        
    def set_dynamics(self, dynamics):
        self.config.dynamics = dynamics
        
    def set_controller(self, controller):
        self.config.controller = controller
        
    def set_state(self, state):
        self.state = state

    def compute_observations(self):
        data = OpenStruct()
        data.sensels = []
        data.optics = []
        for i, sensor in enumerate(self.config.optics):
            # XXX add translation
            sensor_pose = self.state
            sensor_data = sensor.render(sensor_pose)
            # XXX add derivative
            data.optics.append( OpenStruct(**sensor_data) )
            data.sensels.extend(data.optics[i].luminance)

        data.rangefinder = []
        for i, sensor in enumerate(self.config.rangefinder):
            # XXX add translation
            sensor_pose = self.state
            sensor_data = sensor.render(sensor_pose)
            # XXX add derivative
            data.rangefinder.append( OpenStruct(**sensor_data) )
            data.sensels.extend(data.rangefinder[i].readings)

        return data
            
        
        