import aprofiles as apro
import pytest
import numpy as np


@pytest.fixture
def subtime_profiles():
    path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
    profiles = apro.reader.ReadProfiles(path).read()
    # subset time to make calculation quicker
    datetime1 = np.datetime64("2021-09-09T14:00:00")
    datetime2 = np.datetime64("2021-09-09T16:00:00")
    profiles.data = profiles.data.sel(time=slice(datetime1, datetime2))
    return profiles


def test_detect_pbl(subtime_profiles):
    # call foc detection method
    apro.detection.pbl.detect_pbl(subtime_profiles, under_clouds=False)
    pbl = subtime_profiles.data.pbl.data
    # test values
    # Full SNR windows exclude low-altitude candidates near the profile edge.
    assert np.count_nonzero(np.isfinite(pbl)) == 9
    assert np.nanmean(pbl) == pytest.approx(1704.985, abs=0.01)


def test_pbl_with_single_cloud_pixel(subtime_profiles):
    shape = subtime_profiles.data.attenuated_backscatter_0.shape
    clouds = np.zeros(shape, dtype=bool)
    clouds[0, 100] = True
    subtime_profiles.data["clouds"] = (("time", "altitude"), clouds)

    subtime_profiles.pbl(zmin=200, zmax=3000, under_clouds=True, min_snr=2.)

    assert subtime_profiles.data.pbl.shape == (shape[0],)
    if np.isfinite(subtime_profiles.data.pbl.data[0]):
        assert subtime_profiles.data.pbl.data[0] <= subtime_profiles.data.altitude.data[100]
