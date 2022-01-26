# @author Augustin Mortier
# @desc A-Profiles - Utils

import numpy as np

def get_true_indexes(mask):
    # mask: list of Bool
    # returns a list indexes where the mask is True
    return [i for i, x in enumerate(mask) if x]

def make_mask(length, indexes_where_True):
    # length: int: length of the mask
    # indexes_where_true: list
    mask = np.asarray([False for x in np.ones(length)])
    mask[indexes_where_True] = len(indexes_where_True) * [True]
    return mask
