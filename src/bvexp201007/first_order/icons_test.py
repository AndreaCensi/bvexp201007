from pybv_experiments.pieces import vehicles_list_A
from pybv.drawing.icons import draw_vehicle_icon


vehicle_list = vehicles_list_A()

for vname, vehicle in vehicle_list:
    print vname
    draw_vehicle_icon(vehicle, "%s.pdf" % vname)