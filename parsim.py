from pybv.simulation import is_state_available, save_state, load_state, remove_state
from time import time
import re
from pybv.simulation.utils import create_progress_bar


class ParsimException(Exception):
    pass

class Computation:
    id2computations = {}
    
    def __init__(self, job_id, depends, command, args, kwargs, yields=False):
        self.job_id = job_id
        self.depends = depends
        self.needed_by = []
        self.command = command
        self.kwargs = kwargs 
        self.args = args
        self.yields = yields
        
    def compute(self, deps, previous_result=None):
        print "make %s" % self.job_id
        kwargs = dict(**self.kwargs)
        if previous_result is not None:
            kw = 'previous_result'
            available = self.command.func_code.co_varnames
            
            if not kw in available:
                raise ParsimException(('Function does not have a "%s" argument, necessary'+
                                  'for makemore (args: %s)') % (kw, available))
            kwargs[kw] = previous_result
            
        if len(deps) == 0:
            return self.command(*self.args, **kwargs)
        elif len(deps) == 1:
            return self.command(deps[0], *self.args, **kwargs)
        else:
            return self.command(deps, *self.args, **kwargs)
        
    
class Cache:
    def __init__(self, timestamp, user_object, computation, finished):
        self.timestamp = timestamp
        self.user_object = user_object
        self.finished = finished
        self.computation = computation
        
def add_computation(depends, parsim_job_id, command, *args, **kwargs):
    job_id = parsim_job_id
    
    if job_id in Computation.id2computations:
        raise ParsimException('Computation %s already defined.' % job_id)
    
    if not isinstance(depends, list):
        depends = [depends]
    depends = [Computation.id2computations[x] for x in depends]
    
    c = Computation(job_id=job_id,depends=depends,
                    command=command, args=args, kwargs=kwargs)
    Computation.id2computations[job_id] = c
        # TODO: check for loops     
    for x in depends:
        x.needed_by.append(c)
    return c

def up_to_date(job_id):
    """ Check that the job is up to date. 
    We are up to date if:
    1) we have a cache AND the timestamp is not 0  AND finished = True
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
        if cache.finished == False:
            return False, 'Previous job not finished'
        
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
    
from types import GeneratorType

def make(job_id, more=False):
    """ Returns the user-object """
    up, reason = up_to_date(job_id)
    if up and not more:
        return get_cache(job_id).user_object
    else:
        if up and more: 
            reason = 'want more'
        print "Making %s (%s)" % (job_id, reason)
        computation = Computation.id2computations[job_id]
        deps = []
        for child in computation.depends:
            deps.append(make(child.job_id))
            
        cache_available = is_cache_available(job_id)
        if cache_available:
            cache = get_cache(job_id)
            not_finished = not cache.finished
             
        if more and (not cache_available or (cache_available and not_finished) ): 
            raise ParsimException('You asked for more of %s, but nothing found.' %
                                      job_id) 
        assert( not more or cache_available)
        
        if more or (cache_available and not_finished):
            previous_user_object = cache.user_object
        else:
            previous_user_object = None
                
        result = computation.compute(deps, previous_user_object)
        if type(result) == GeneratorType:
            pbar = None
            try:
                while True:
                    next = result.next()
                    if isinstance(next, tuple):
                        if len(next) != 3:
                            raise ParsimException('If computation yields a tuple, ' +
                                                  'should be a tuple with 3 elemnts.'+
                                                  'Got: %s' % next)
                        user_object, num, total = next
                        if pbar is None:
                            pbar = create_progress_bar(job_id, total)
                        pbar.update(num)
                        # pbar
                        cache = Cache(timestamp=time(),user_object=user_object,
                                      computation=computation, finished=False)
                        set_cache(job_id, cache)

            except StopIteration:
                pass
        else:
            pbar = create_progress_bar(job_id, 1)
            pbar.update(0)
            user_object = result
            pbar.update(1)
            
        timestamp = time()
        cache = Cache(timestamp=timestamp,user_object=user_object,
                      computation=computation, finished=True)
        set_cache(job_id, cache)
        return cache.user_object

def make_more(job_id):
    return make(job_id, more=True)

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


############### Saving and loading state
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
################## 



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
            
    if commands[0] == 'more':
        job_list = parse_job_list(commands[1:])
        if len(job_list) == 0:
            job_list = bottom_targets()
            
        for job in job_list:
            make_more(job)
        
    
    
    
    