# @author Augustin Mortier
# @desc A-Profiles - AeronetsData class

import copy

import numpy as np
import pandas as pd
import xarray as xr
from tqdm import tqdm

import aprofiles as apro


class AeronetData:
    """Base class representing profiles data returned by :class:`aprofiles.io.reader.ReadAeronet`."""

    def __init__(self, data):
        self.data = data
        raise NotImplementedError("AeronetData is not implemented yet")

    @property
    def data(self):
        """Data attribute (instance of :class:`xarray.Dataset`)"""
        return self._data

    @data.setter
    def data(self, data):
        if not isinstance(data, xr.Dataset):
            raise ValueError("Wrong data type: an xarray Dataset is expected.")
        self._data = data


def _main():
    import aprofiles as apro

    path = "data/e-profile/2021/09/08/L2_0-20000-006735_A20210908.nc"
    path = "data/e-profile/2021/09/09/L2_0-20000-001492_A20210909.nc"
    profiles = apro.reader.ReadProfiles(path).read()

    # basic corrections
    profiles.extrapolate_below(z=150.0, inplace=True)
    profiles.desaturate_below(z=4000.0, inplace=True)
    # detection
    profiles.foc(method="cloud_base", zmin_cloud=200)
    profiles.clouds(zmin=300, thr_noise=5, thr_clouds=4, verbose=True)
    profiles.plot(show_foc=True, show_clouds=True, log=True, vmin=1e-2, vmax=1e1)


if __name__ == "__main__":
    _main()
