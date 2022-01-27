# @author Augustin Mortier
# @desc A-Profiles - Reference Altitude

import numpy as np
from aprofiles import utils


def get_iref(data, imin, imax, min_snr):
    """Function that returns best index to be used for initializing the Klett backward inversion.

    Args:
        data (1D Array): Attenuated backscatter profile.
        imin (int): Minimum index of the altitude range in which to look for the reference point.
        imax (int): Maximum index of the altitude range in which to look for the reference point.
        min_snr (float): Minimum SNR required to return a valid value.

    Returns:
        int: index of the reference point.
    """
    # function that returns best index to be used for initializing the Klett backward inversion

    # it is important to copy the data not to modify it outside of the function
    data = data.copy()

    # check if imin below imax
    if imin < imax:
        # limit from imin to imax
        maxdata = np.nanmax(data)
        data[0:imin] = maxdata
        data[imax:] = maxdata

        # running average
        from scipy.ndimage.filters import uniform_filter1d

        avg_data = uniform_filter1d(data, size=3)

        if not np.isnan(np.nanmin(avg_data)):
            # get minimum from the averaged signal
            ilow = np.nanargmin(avg_data)

            # around minimum, get index of closest signal to average signal
            n_around_min = 3
            iclose = np.nanargmin(
                abs(
                    data[ilow - n_around_min: ilow + n_around_min]
                    - avg_data[ilow - n_around_min: ilow + n_around_min]
                )
            )

            if utils.snr_at_iz(data, iclose, step=4) < min_snr:
                return None
            else:
                return ilow + iclose
        else:
            return None
    else:
        return None
