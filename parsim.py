from pybv.simulation import is_state_available, save_state, load_state, remove_state
from time import time
import re

class ParsimException(Exception):
    pass

class Computation:
    id2computations = {}
    
    def __init__(self, job_id, depends, command, args, kwargs):
        self.job_id = job_id
        self.depends = depends
        self.needed_by = []
        self.command = command
        self.kwargs = kwargs 
        self.args = args
        
    def compute(self, deps):
        print "make %s" % self.job_id
        if len(deps) == 0:
            return self.command(*self.args, **self.kwargs)
        elif len(deps) == 1:
            return self.command(deps[0], *self.args, **self.kwargs)
        else:
            return self.command(deps, *self.args, **self.kwargs)
    
class Cache:
    def __init__(self, timestamp, user_object, computation):
        self.timestamp = timestamp
        self.user_object = user_object
        self.computation = computation
        
def add_computation(depends, parsim_job_id, command, *args, **kwargs):
    job_id = parsim_job_id
    # print "%s -> %s"  % (depends, job_id)
    if not isinstance(depends, list):
        depends = [depends]
    
    depends = [Computation.id2computations[x] for x in depends]
    
    c = Computation(job_id=job_id,depends=depends,
                    command=command, args=args, kwargs=kwargs)
    Computation.id2computations[job_id] = c
    
    # print Computation.id2computations.keys()
    # TODO: check for loops     
    for x in depends:
        x.needed_by.append(c)

def job2cachename(job_id):
    return 'parsim_%s' % job_id

def get_cache(name):
    assert(is_cache_available(name))
    return load_state(job2cachename(name))

def delete_cache(name):
    assert(is_cache_available(name))
    remove_state(job2cachename(name))
    
def is_cache_available(name):
    return is_state_available(job2cachename(name))
    
def set_cache(name, value): 
    return save_state(job2cachename(name), value)

def up_to_date(job_id):
    """ Check that the job is up to date. 
    We are up to date if:
    1) we have a cache AND the timestamp is not 0 AND
    2) the children are up to date AND
    3) the children timestamp is older than this timestamp AND
    
    Returns:
    
        boolean, explanation 
    
    """ 
    if is_cache_available(job_id): 
        cache = get_cache(job_id)
        this_timestamp = cache.timestamp
        if this_timestamp == 0:
            return False, 'Forced to remake'
        
        computation = Computation.id2computations[job_id]
        for child in computation.depends:
            if not up_to_date(child.job_id):
                return False, 'Child %s not up to date.' % child.job_id
            else:
                child_timestamp = get_cache(child.job_id).timestamp
                if child_timestamp > this_timestamp:
                    return False, 'Child %s has been updated.' % child.job_id
                
        # TODO: Check arguments!!
        return True, ''
    else:
        return False, 'Cache not found'
    
    
def make(job_id):
    """ Returns the user-object """
    # print "Make %s" % job_id
    up, reason = up_to_date(job_id)
    if up:
    #    print "Job %s is up to date" % job_id
        return get_cache(job_id).user_object
    else:
        print "Making %s (%s)" % (job_id, reason)
        computation = Computation.id2computations[job_id]
        deps = []
        for child in computation.depends:
            deps.append(make(child.job_id))
    
        user_object = computation.compute(deps)
        timestamp = time()
        cache = Cache(timestamp=timestamp,user_object=user_object,
                      computation=computation)
        set_cache(job_id, cache)
        return cache.user_object
        
def make_all():
    targets = top_targets()
    for t in targets:
        make(t)
    
def remake(job_id):
    up, reason = up_to_date(job_id)

    if up:
        # invalidate the timestamp
        cache = get_cache(job_id)
        cache.timestamp = 0
        set_cache(job_id, cache) 
        up, reason = up_to_date(job_id)
        assert(not up)
        
    return make(job_id)
    
def remake_all():
    for job in bottom_targets():
        remake(job)
        
    
def top_targets():
    """ Returns a list of all jobs which are not needed by anybody """
    return [x.job_id for x in Computation.id2computations.values() if len(x.needed_by) == 0]
    
def bottom_targets():
    """ Returns a list of all jobs with no dependencies """
    return [x.job_id for x in Computation.id2computations.values() if len(x.depends) == 0]

import sys

def reg_from_shell_wildcard(arg):
    """ Returns a regular expression from a shell wildcard expression """
    return re.compile('\A' + arg.replace('*', '.*') + '\Z')
                      
def parse_job_list(argv):
    jobs = []
    for arg in argv:
        if arg.find('*') is not None:
            reg = reg_from_shell_wildcard(arg)
            matches = [x for x in Computation.id2computations.keys() 
                       if reg.match(x) ]
            jobs.extend(matches)
        else:
            if not arg in Computation.id2computations:
                raise ParsimException('Job %s not found (%s)' %
                                       (arg, Computation.id2computations.keys())) 
            jobs.append(arg)
    return jobs

def make_sure_cache_is_sane():
    """ Checks that the cache is sane, deletes things that cannot be open """
    for job_id in Computation.id2computations.keys():
        if is_cache_available(job_id):
            try:
                get_cache(job_id)
            except:
                print "Cache %s not sane. Deleting." % job_id
                delete_cache(job_id)


def interpret_commands():
    make_sure_cache_is_sane()
    
    
    commands = sys.argv[1:]
    if len(commands) == 0:
        make_all()
        sys.exit(0)
        
    if commands[0] == 'list':
        job_list = parse_job_list(commands[1:])
        if len(job_list) == 0:
            job_list = Computation.id2computations.keys()
        print job_list

    if commands[0] == 'make':
        job_list = parse_job_list(commands[1:])
        if len(job_list) == 0:
            make_all()
            sys.exit(0)
        for job in job_list:
            make(job)
        sys.exit(0)
        
    if commands[0] == 'remake':
        job_list = parse_job_list(commands[1:])
        if len(job_list) == 0:
            remake_all()
            sys.exit(0)
            
        for job in job_list:
            remake(job)
        make_all()
        sys.exit(0)
            
    if commands[0] == 'more':
        pass
     
            
        
    
    
    
    