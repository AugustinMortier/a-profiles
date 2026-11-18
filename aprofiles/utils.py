# @author Augustin Mortier
# @desc A-Profiles - Utils

import numpy as np
import os
import operator

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

def _snr_windows(windows):
    results = np.full(windows.shape[0], np.nan)
    valid = np.any(~np.isnan(windows), axis=1)
    if np.any(valid):
        with np.errstate(invalid="ignore", divide="ignore", over="ignore"):
            means = np.nanmean(windows[valid], axis=1)
            stds = np.nanstd(windows[valid], axis=1)
            results[valid] = np.divide(
                means, stds, out=np.full(means.shape, np.nan), where=stds != 0
            )
    return results


def _snr_step(step):
    step = operator.index(step)
    if step < 0:
        raise ValueError("step must be non-negative")
    return step


def snr_profile(array, step):
    """Return local mean / standard deviation for each gate of a 1D profile.

    The symmetric window contains ``2 * step + 1`` gates. NaNs are ignored;
    incomplete windows, all-NaN windows and zero standard deviations produce NaN.
    This local variability includes real signal structure, not only noise.
    """
    step = _snr_step(step)
    array = np.asarray(array)
    if array.ndim != 1:
        raise ValueError("array must be one-dimensional")
    result = np.full(array.shape, np.nan)
    width = 2 * step + 1
    if width <= len(array):
        windows = np.lib.stride_tricks.sliding_window_view(array, width)
        result[step:len(array) - step] = _snr_windows(windows)
    return result


def snr_at_iz(array, iz, step):
    """Return the local mean / standard deviation at one gate.

    Uses the same symmetric window and NaN handling as ``snr_profile``.
    Incomplete windows, all-NaN windows and zero standard deviations return NaN.

    Args:
        array (array-like): One-dimensional signal profile.
        iz (int): Index where to calculate SNR.
        step (int): Number of gates on each side of the index.
    """
    step = _snr_step(step)
    iz = operator.index(iz)
    array = np.asarray(array)
    if array.ndim != 1:
        raise ValueError("array must be one-dimensional")
    if iz < 0 or iz >= len(array):
        raise IndexError("iz is outside the profile")
    if iz < step or iz + step >= len(array):
        return np.nan
    return _snr_windows(array[np.newaxis, iz - step:iz + step + 1])[0]

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