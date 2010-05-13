from PIL import Image #@UnresolvedImport
import os

import numpy
from numpy import maximum, minimum, isnan, zeros #@PydevCodeAnalysisIgnore

from pybv.utils.numpy_utils import gt, require_shape

def colormap_rgba(values, colors, invalid_color=[255, 255, 0, 255],
                   nan_color=[0, 0, 0, 0]):
    # entris = [ (min, max, [r,g,b,a]),... ]
    require_shape((gt(0), gt(0)), values)
    h, w = values.shape
    res = numpy.zeros(shape=(h, w, 4), dtype='uint8')
    for i in range(h):
        for j in range(w):
            chosen = invalid_color
            val = values[i, j]
            for vmin, vmax, color in colors:
                if vmin <= val <= vmax:
                    chosen = color
                    break
            if isnan(val):
                chosen = nan_color
            res[i, j, :] = chosen
    return res


def posneg(value, maxval=None, depth=3):
    """ Converts a 2D vlaue to normalized uint8 RGB red=positive, blue=negative 0-255
    
    Args:
        depth (int): 3 if RGB, 4 if RGBA
    """
    value = value.squeeze()
    assert(len(value.shape) == 2)
    
    if maxval is None:
        maxval = numpy.max(abs(value))
        if maxval == 0:
            raise ValueError('You asked to normalize a matrix which is all 0')

    positive_part = abs((maximum(value, 0) / maxval) * 255).astype('uint8')
    negative_part = abs((minimum(value, 0) / maxval) * 255).astype('uint8')
    result = zeros((value.shape[0], value.shape[1], depth), dtype='uint8')
    #print negative_part.shape, positive_part.shape, result.shape
    if 0:
        result[:, :, 0] = positive_part[:, :]
        result[:, :, 2] = negative_part[:, :]
    else:
        anysign = maximum(positive_part, negative_part)
        result[:, :, 0] = 255 - negative_part[:, :]
        result[:, :, 1] = 255 - anysign
        result[:, :, 2] = 255 - positive_part[:, :]
        
        
    if depth == 4:
        result[:, :, 3] = 255
    
    return result



# XXX make this configurable
Basepath = '~/parsim_storage/'

def get_filename(path, extension):
    path = list(path)
    path[-1] = path[-1] + ".%s" % extension
    path2 = [Basepath] # XXX insert 
    path2.extend(path)
    filename = os.path.join(*path2)
    filename = os.path.expanduser(filename)
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    return filename

def image_newer_than_timestamp(path, timestamp):
    for extension in ['eps', 'pdf', 'png']:
        filename = get_filename(path, extension)
        if os.path.exists(filename) and \
            os.path.getmtime(filename) > timestamp:
            return True
    return False
    
def Image_from_array(a):
    ''' Converts an image in a numpy array to an Image instance.
        Accepts:  h x w      255   grayscale 
        Accepts:  h x w x 3  255  rgb '''
    if len(a.shape) == 2:
        height, width = a.shape
        rgba = numpy.zeros((height, width, 4), dtype='uint8')
        rgba[:, :, 0] = a
        rgba[:, :, 1] = a
        rgba[:, :, 2] = a
        rgba[:, :, 3] = 255
    else:
        require_shape((gt(0), gt(0), 4), a)
        height, width = a.shape[0:2]
        rgba = a.astype('uint8')
    
    require_shape((gt(0), gt(0), 4), rgba) 
    
    im = Image.frombuffer("RGBA", (width, height), rgba.data,
                           "raw", "RGBA", 0, 1)
    return im

def save_posneg_matrix(path, value, maxvalue=None):
    if isnan(value).any():
        raise ValueError('Found NAN in image %s ' % os.path.join(path))

    if isinstance(path, list):
        # XXX remove this eventually
        filename = get_filename(path, 'png')
    else:
        filename = path

    converted = posneg(value, depth=4, maxval=maxvalue)
    Image_from_array(converted).save(filename)
 
    

def save_probability_matrix(filename, value):
    if isnan(value).any():
        raise ValueError('Found NAN in image %s ' % os.path.join(path))

    value = value * 255
    
    Image_from_array(value).save(filename) 
    
    # TODO draw colorscale
    
def save_success_matrix(filename, value):
    red = [255, 0, 0, 255]
    magenta = [186, 50, 50, 255]
    yellow = [255, 255, 0, 255]
    orange = [255, 164, 18, 255]
    blue = [0, 0, 255, 255]
    bluegreen = [255, 255, 120, 255]
    darkgreen = [0, 100, 0 , 255]
    green = [0, 255, 0, 255]
    
    colors = [(0, 0.001, red), (0.001, 0.05, magenta), (0.05, 0.25, yellow),
              (0.25, 0.50, orange), (0.5, 0.75, blue), (0.75, 0.95, bluegreen),
              (0.95, 0.99, darkgreen), (0.99, 1, green) ]
    rgba = colormap_rgba(value, colors)
    Image_from_array(rgba).save(filename) 
