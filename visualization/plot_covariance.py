from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np


def plot_covariance(covariance, directions=None):
    
    fig = plt.figure()
    ax = Axes3D(fig)

    n = covariance.shape[0]
    if directions is None:
        directions = range(1,n)
        
    X = directions
    Y = directions
    X, Y = np.meshgrid(X, Y)
    Z = covariance
    ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.jet)

    plt.show()
