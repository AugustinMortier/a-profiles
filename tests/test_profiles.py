import aprofiles as apro
import pytest
import xarray as xr
import numpy as np


# arrange test
@pytest.fixture
def profiles():
    path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
    profiles = apro.reader.ReadProfiles(path).read()
    # subset altitude to make calculation quicker
    profiles.data = profiles.data.sel(altitude=slice(0, 1000))
    return profiles

# test class
class TestProfilesData:
    def test_snr(self, profiles):
        profiles.snr()
        snr = profiles.data.snr
        # test types
        assert type(snr) is xr.core.dataarray.DataArray
        assert type(snr.data) is np.ndarray
        # test values
        assert np.mean(snr.data) == 8.236267199712106
    
    def test_gaussian_filter(self, profiles):
        filter = profiles.gaussian_filter(sigma=0.25, var="attenuated_backscatter_0")
        # test attributes
        assert filter.data.attenuated_backscatter_0.attrs['gaussian_filter'] == 0.25
        # test values
        assert np.mean(filter.data.attenuated_backscatter_0.data) == 22.678106250188538

    def test_time_avg(self, profiles):
        avg_profiles = profiles.time_avg(10, var="attenuated_backscatter_0")
        # test attributes
        assert avg_profiles.data.attenuated_backscatter_0.attrs['time averaged (minutes)'] == 10

    def test_extrapolate_below(self, profiles):
        extrap_profiles = profiles.extrapolate_below(var="attenuated_backscatter_0", z=150, method="cst")
        # test attributes
        assert extrap_profiles.data.attenuated_backscatter_0.attrs['extrapolation_low_layers_altitude_agl'] == 150
        assert extrap_profiles.data.attenuated_backscatter_0.attrs['extrapolation_low_layers_method'] == 'cst'
        # test if single value for 5 first indexes
        assert len(np.unique(extrap_profiles.data.attenuated_backscatter_0.data[0][0:5])) == 1
