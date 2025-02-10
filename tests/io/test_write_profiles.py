import shutil

import aprofiles as apro
import numpy as np
import pytest
import xarray as xr
from aprofiles import utils
from aprofiles.io import write_profiles


# arrange test
@pytest.fixture
def profiles():
    path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
    profiles = apro.reader.ReadProfiles(path).read()
    # subset time to make calculation quicker
    datetime1 = np.datetime64('2021-09-09T14:00:00')
    datetime2 = np.datetime64('2021-09-09T16:00:00')
    profiles.data.sel(time=slice(datetime1, datetime2))
    # data processing
    profiles.extrapolate_below(z=150, inplace=True)
    profiles.clouds(zmin=300, thr_noise=5, thr_clouds=4)
    profiles.foc(zmin_cloud=200)
    profiles.pbl(zmin=200, zmax=3000, under_clouds=True)
    profiles.inversion()
    return profiles

# test class
def test_write(profiles):
    base_dir = './tmp'
    # call writing method
    write_profiles.write(profiles, base_dir, verbose=False)
    # check if file exists
    check_file = utils.file_exists(f'{base_dir}/2021/09/09/AP_0-20000-0-01492-A-2021-09-09.nc')
    assert check_file == True
    # remove created folder
    shutil.rmtree(base_dir)

