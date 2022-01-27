import aprofiles as apro
import pytest
import numpy as np


@pytest.fixture
def subtime_profiles():
    path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
    profiles = apro.reader.ReadProfiles(path).read()
    # subset time to make calculation quicker
    datetime1 = np.datetime64('2021-09-09T21:00:00')
    datetime2 = np.datetime64('2021-09-09T23:00:00')
    profiles.data = profiles.data.sel(time=slice(datetime1, datetime2))
    return profiles

def test_detect_foc(subtime_profiles):
    # call foc detection method
    apro.detection.foc.detect_foc(subtime_profiles)
    foc = subtime_profiles.data.foc.data
    # test values
    assert np.round(np.mean(foc), 4) == 0.2083

def test__detect_fog_from_cloud_base_height(subtime_profiles):
    # call method
    zmin_cloud = 200.
    foc = apro.detection.foc._detect_fog_from_cloud_base_height(subtime_profiles, zmin_cloud)
    # test values
    assert np.round(np.nanmean(foc), 3) == 0.208

def test__detect_fog_snr(subtime_profiles):
    # call method
    z_snr = 2000.
    var = "attenuated_backscatter_0"
    min_snr = 2.
    foc = apro.detection.foc._detect_fog_from_snr(subtime_profiles, z_snr, var, min_snr)
    # test values
    assert np.round(np.nanmean(foc), 3) == 0.167
