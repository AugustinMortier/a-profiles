# @author Augustin Mortier
# @desc A-Profiles - Utils

import numpy as np

def get_true_indexes(mask):
    # mask: list of Bool
    # returns a list indexes where the mask is True
    return [i for i, x in enumerate(mask) if x]
