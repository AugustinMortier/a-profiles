# @author Augustin Mortier
# @desc A-Profiles - Utils

import numpy as np
import os

def get_true_indexes(mask):
    """
    Returns indexes of a list of boolean values where the values are True.

    Args:
        - mask (list): list of Bool.
    """
    return [i for i, x in enumerate(mask) if x]

def make_mask(length, indexes_where_True):
    """
    Returns a list of Bool of a given length with True values at given indexes.

    Args:
        - length (int): length of the list.
        - indexes_where_True (list): indexes where the values are True.
    """
    # length: int: length of the mask
    # indexes_where_true: list
    mask = np.asarray([False for x in np.ones(length)])
    mask[indexes_where_True] = len(indexes_where_True) * [True]
    return mask

def file_exists(path):
    """
    Returns True is file exists.

    Args:
        - path (str): path of the file to be checked.
    """
    return os.path.exists(path)
