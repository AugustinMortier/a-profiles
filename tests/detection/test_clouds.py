import aprofiles as apro
import pytest
import numpy as np


@pytest.fixture
def subtime_profiles():
    path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
    profiles = apro.reader.ReadProfiles(path).read()
    # subset time to make calculation quicker
    datetime1 = np.datetime64('2021-09-09T14:00:00')
    datetime2 = np.datetime64('2021-09-09T16:00:00')
    profiles.data = profiles.data.sel(time=slice(datetime1, datetime2))
    return profiles

def test_detect_clouds_dec(subtime_profiles):
    # call clouds detection method
    apro.detection.clouds.detect_clouds(subtime_profiles, method='dec')
    clouds = subtime_profiles.data.clouds.data
    
    # test values
    assert np.round(np.mean(clouds), 4) > 0

def test_detect_clouds_vg(subtime_profiles):
    # call clouds detection method
    apro.detection.clouds.detect_clouds(subtime_profiles, method='vg')
    clouds = subtime_profiles.data.clouds.data
    
    # test values
    assert np.round(np.mean(clouds), 4) > 0


def test_dec_filters_individual_pixels_by_snr(subtime_profiles, monkeypatch):
    apro.detection.clouds.detect_clouds(subtime_profiles, method="dec")
    unfiltered = subtime_profiles.data.clouds.data.copy()
    assert unfiltered.any()

    def snr_by_altitude(data, iz, step):
        assert step == 10
        return (1.0, 2.0, 3.0, np.nan)[iz % 4]

    monkeypatch.setattr(apro.utils, "snr_at_iz", snr_by_altitude)
    apro.detection.clouds.detect_clouds(subtime_profiles, method="dec", min_snr=2.0)

    expected = unfiltered & (np.arange(unfiltered.shape[1]) % 4 != 0)
    assert np.any(unfiltered & ~expected)
    assert expected.any()
    assert np.any(unfiltered[:, 3::4])
    np.testing.assert_array_equal(subtime_profiles.data.clouds.data, expected)


@pytest.mark.parametrize("min_snr", [0.0, -1.0, None])
def test_dec_skips_snr_filter_when_disabled(subtime_profiles, monkeypatch, min_snr):
    def unexpected_snr(*args, **kwargs):
        raise AssertionError("SNR should not be calculated when filtering is disabled")

    monkeypatch.setattr(apro.utils, "snr_at_iz", unexpected_snr)
    apro.detection.clouds.detect_clouds(subtime_profiles, method="dec", min_snr=min_snr)
    assert subtime_profiles.data.clouds.data.any()