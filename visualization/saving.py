import numpy

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

    positive_part = numpy.abs((numpy.maximum(value, 0)/maxval)*255).astype('uint8')
    negative_part = numpy.abs((numpy.minimum(value, 0)/maxval)*255).astype('uint8')
    result = numpy.zeros((value.shape[0], value.shape[1], depth), dtype='uint8')
    #print negative_part.shape, positive_part.shape, result.shape
    if 0:
        result[:,:,0] = positive_part[:,:]
        result[:,:,2] = negative_part[:,:]
    else:
        anysign = numpy.maximum(positive_part, negative_part)
        result[:,:,0] = 255-negative_part[:,:]
        result[:,:,1] = 255 - anysign
        result[:,:,2] = 255-positive_part[:,:]
        
        
    if depth == 4:
        result[:,:,3] = 255
    
    return result

from PIL import Image
import os 

basepath = '~/svn/cds/pri/bv/src/pybv_experiments_results'

def get_filename(path, extension):
    path[-1] += ".%s" % extension
    filename= os.path.join(basepath, *path)
    filename = os.path.expanduser(filename)
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    return filename

import sys
def should_I_force_replot():
    return any([x == 'replot' for x in sys.argv])
    
def save_posneg_matrix(path, value, maxvalue=None,text=None):
    if numpy.isnan(value).any():
        raise ValueError('Found NAN in image %s ' % os.path.join(path) )
    
    filename = get_filename(path, 'png')
    force_replot = should_I_force_replot()
    if (not force_replot) and os.path.exists(filename):
        print "Already exists %s " % os.path.join(*path)
        return
        
    converted = posneg(value, depth=4, maxval=maxvalue)
    height,width=value.shape
    im = Image.frombuffer("RGBA", (width,height), converted.data, "raw", "RGBA", 0, 1)
    print "Printing %s " % os.path.join(*path)
    im.save(filename)
    
    # TODO draw colorscale
    
    
    
