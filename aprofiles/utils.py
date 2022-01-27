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

def snr_at_iz(array, iz, step):
    """
    Returns the SNR from an array calculated at iz with step points above and below.

    Args:
        - array (list): data array.
        - iz (int): index where to calculate SNR.
        - step (int): number of steps to be used for SNR calculation.
    """
    # calculates the snr from array at iz around step points
    gates = np.arange(iz - step, iz + step)
    indexes = [i for i in gates if i > 0 and i < len(array)]
    mean = np.nanmean(array[indexes])
    std = np.nanstd(array[indexes], ddof=0)
    if std != 0:
        return mean / std
    else:
        return 0

def gaussian(x, mu, sig, norm):
    """1D Gaussian function

    Args:
        x (1D-Array): array of values for which to return the Gaussian function.
        mu (float): Mean
        sig (float): Standard deviation
        norm (float): Normalization factor

    Returns:
        1D-Array: Gaussian distribution
    """
    return (norm / (np.sqrt(2 * np.pi) * sig)) * np.exp(
        -((x - mu) ** 2 / (2 * sig ** 2))
    )