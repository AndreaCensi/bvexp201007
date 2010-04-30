import numpy
from PIL import Image #@UnresolvedImport
import os

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

    positive_part = numpy.abs((numpy.maximum(value, 0) / maxval) * 255).astype('uint8')
    negative_part = numpy.abs((numpy.minimum(value, 0) / maxval) * 255).astype('uint8')
    result = numpy.zeros((value.shape[0], value.shape[1], depth), dtype='uint8')
    #print negative_part.shape, positive_part.shape, result.shape
    if 0:
        result[:, :, 0] = positive_part[:, :]
        result[:, :, 2] = negative_part[:, :]
    else:
        anysign = numpy.maximum(positive_part, negative_part)
        result[:, :, 0] = 255 - negative_part[:, :]
        result[:, :, 1] = 255 - anysign
        result[:, :, 2] = 255 - positive_part[:, :]
        
        
    if depth == 4:
        result[:, :, 3] = 255
    
    return result




basepath = '~/parsim_storage/'

def get_filename(path, extension):
    path = list(path)
    path[-1] = path[-1] + ".%s" % extension
    filename = os.path.join(basepath, *path)
    filename = os.path.expanduser(filename)
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    return filename

def image_newer_than_timestamp(path, timestamp):
    for extension in ['eps', 'pdf', 'png']:
        filename = get_filename(path, extension)
        if os.path.exists(filename) and (os.path.getmtime(filename) > timestamp):
            return True
    return False
    
def save_posneg_matrix(path, value, maxvalue=None):
    if numpy.isnan(value).any():
        raise ValueError('Found NAN in image %s ' % os.path.join(path))
    
    
    filename = get_filename(path, 'png')

    converted = posneg(value, depth=4, maxval=maxvalue)
    height, width = value.shape
    im = Image.frombuffer("RGBA", (width, height), converted.data, "raw", "RGBA", 0, 1)
    print "Printing %s " % os.path.join(*path)
    im.save(filename)
    
    # TODO draw colorscale
    
    
    
    
