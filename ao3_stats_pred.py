from ao3_stats_classes import *



###################
##   VERSION 2   ##
##  (MISC FUNC)  ##
###################

# Created 30/08/2018
# Now with very beautiful soup





#################
##    TYPE     ##
##  CHECKING   ##
#################

def dict_to_list(x, obj_name, raise_e = True):
    '''
    Converts dictionaries to iterable list
    (Leaves lists and tuples alone)
    '''
    if isinstance(x, list) or isinstance(x, tuple):
        return x
    elif isinstance(x, dict):
        return list(x.values())
    elif raise_e:
        raise TypeError("{} should either be an iterable or a dictionary object".format(obj_name))


def is_num(x):
    return isinstance(x, int) or \
           isinstance(x, float) or \
           isinstance(x, NumOrQ)
