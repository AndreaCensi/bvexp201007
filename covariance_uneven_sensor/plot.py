
import go as result

from pybv.visualization import plot_covariance
from pylab import *
figure()
plot_covariance(result.result_sensels.cov_sensels)

figure()
plot_covariance(result.result_luminance.cov_luminance, result.vehicle2.config.optics[0].directions)

figure()
plot_covariance(result.result_readings.cov_readings, sensor.directions)


