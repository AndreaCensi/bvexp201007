from numpy import  random
from compmake import comp, comp_prefix, set_namespace, time_to_define_jobs

from pybv.worlds import create_random_world, get_safe_pose
from pybv.simulation import random_motion_simulation, random_pose_simulation

from pybv_experiments import vehicles_list_A 
from pybv_experiments.first_order.normalize_tensor import normalize_tensor
from pybv_experiments.first_order.compute_fields import compute_fields, \
    create_report_fields
from pybv_experiments.covariance import SenselCovariance

from pybv.sensors.textured_raytracer import TexturedRaytracer 
from pybv_experiments.covariance.first_order_sensels_normalize import  \
    FirstorderSenselsNormalizeUnif 
from pybv_experiments.first_order.plot_parallel import create_report_tensors, \
    create_report_covariance
from reprep import Node
from reprep.out.html import node_to_html_document
from pybv_experiments.first_order.techreport_figures import create_techreport_figures
from pybv_experiments.analysis.olfaction_tensors \
    import analyze_olfaction_covariance_job
 
 
def my_world_gen():
    return create_random_world(radius=10, num_lines=10, num_circles=10)

class MyPoseGen2:
    def set_map(self, world):
        self.raytracer = TexturedRaytracer()
        self.raytracer.set_map(world)
        
    def generate_pose(self):
        return get_safe_pose(
                             raytracer=self.raytracer,
                             world_radius=9,
                             safe_zone=0.5, num_tries=1000)
    def __eq__(self, other):
        ''' Without parameters, they will always compare true ''' 
        return True 

# Generate commands uniformly between -1,1
def my_random_commands_gen(ninteration, vehicle): #@UnusedVariable
    return  (random.rand(3) - 0.5) * 2

def create_report(id, children):
    print children
    return Node(id=id, children=children)
    
def write_report(report, basename):
    node_to_html_document(report, basename + '.html')


if time_to_define_jobs():
    set_namespace('first_order')
    random_pose_gen = MyPoseGen2() 
    
    random_commands_gen = my_random_commands_gen
    
    num_iterations = 500
    dt = 0.1
     
    vehicle_list = vehicles_list_A()
    all_vehicles_report = []
    
    for vname, vehicle in vehicle_list:
        vname_tex = vname.replace('_', '-')
        comp_prefix(vname)
    
        firstorder_result = comp(
            command=random_motion_simulation,
            world_gen=my_world_gen, vehicle=vehicle,
            random_pose_gen=random_pose_gen,
            num_iterations=num_iterations,
            random_commands_gen=random_commands_gen, dt=dt,
            processing_class=FirstorderSenselsNormalizeUnif,
            job_id='first_order')
    
        report_tensors = comp(create_report_tensors, state=firstorder_result,
             report_id='tensors-natural')
    
        covariance_result = comp(random_pose_simulation,
            world_gen=my_world_gen, vehicle=vehicle,
            random_pose_gen=random_pose_gen,
            num_iterations=num_iterations,
            processing_class=SenselCovariance)
    
        report_covariance = comp(create_report_covariance, state=covariance_result,
                                 report_id='covariance')
        
        normalization_result = \
            comp(normalize_tensor, covariance_result, firstorder_result)
    
        report_tensors_normalized = comp(create_report_tensors, state=normalization_result,
                        report_id='tensors-normalized')
         
    
        fields_result = comp(compute_fields, firstorder_result,
                             world_gen=my_world_gen, job_id='fields')
        
        report_fields = comp(create_report_fields, fields_result,
                             report_id='fields-natural') 
        
        nfields_result = comp(compute_fields, normalization_result,
                              world_gen=my_world_gen, job_id='nfields')
        
        report_nfields = comp(create_report_fields, nfields_result,
                              report_id='fields-normalized')
        
        children = [report_covariance, report_tensors, report_tensors_normalized,
                          report_fields, report_nfields]
        
        if vehicle.config.sensors[0].sensor_type_string() == 'olfaction':
            expectation = comp(analyze_olfaction_covariance_job, covariance_result)
            children.append(expectation)
        
        
        vehicle_report = comp(Node, id=vname, children=children)
        all_vehicles_report.append(vehicle_report)
        
    
    comp_prefix()
    
    first_order_report = comp(create_report, id='first_order',
                              children=all_vehicles_report)
        
        #report.to_latex_document(basename + '.tex')
        
    comp(write_report, first_order_report, "reports/first_order") 

    comp(create_techreport_figures, 'techreport', all_vehicles_report)

#batch_command('make all')
