import aprofiles as apro
import pytest
import xarray as xr
import numpy as np


# arrange test
@pytest.fixture
def cropped_profiles():
    path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
    profiles = apro.reader.ReadProfiles(path).read()
    # subset altitude to make calculation quicker
    profiles.data = profiles.data.sel(altitude=slice(0, 1000))
    return profiles

@pytest.fixture
def profiles():
    path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
    profiles = apro.reader.ReadProfiles(path).read()
    return profiles

# test class
class TestProfilesData:
    def test_snr(self, cropped_profiles):
        cropped_profiles.snr()
        snr = cropped_profiles.data.snr
        # test types
        assert type(snr) is xr.core.dataarray.DataArray
        assert type(snr.data) is np.ndarray
        # test values
        assert np.mean(snr.data) == 8.236267199712106

    def test_gaussian_filter(self, cropped_profiles):
        filter = cropped_profiles.gaussian_filter(sigma=0.25, var="attenuated_backscatter_0")
        # test attributes
        assert filter.data.attenuated_backscatter_0.attrs['gaussian_filter'] == 0.25
        # test values
        assert np.mean(filter.data.attenuated_backscatter_0.data) == 22.678106250188538

    def test_time_avg(self, cropped_profiles):
        avg_profiles = cropped_profiles.time_avg(10, var="attenuated_backscatter_0")
        # test attributes
        assert avg_profiles.data.attenuated_backscatter_0.attrs['time averaged (minutes)'] == 10

    def test_extrapolate_below(self, cropped_profiles):
        extrap_profiles = cropped_profiles.extrapolate_below(var="attenuated_backscatter_0", z=150, method="cst")
        # test attributes
        assert extrap_profiles.data.attenuated_backscatter_0.attrs['extrapolation_low_layers_altitude_agl'] == 150
        assert extrap_profiles.data.attenuated_backscatter_0.attrs['extrapolation_low_layers_method'] == 'cst'
        # test if single value for 5 first indexes
        assert len(np.unique(extrap_profiles.data.attenuated_backscatter_0.data[0][0:5])) == 1

    def test_range_correction(self, cropped_profiles):
        range_correc_profiles = cropped_profiles.range_correction(var="attenuated_backscatter_0")
        # test attributes
        assert range_correc_profiles.data.attenuated_backscatter_0.attrs['range correction'] is True
        assert range_correc_profiles.data.attenuated_backscatter_0.attrs['units'] is None

    def test_desaturate_below(self, profiles):
        desaturate_profiles = profiles.desaturate_below(var="attenuated_backscatter_0", z=4000.)
        # test attributes
        assert desaturate_profiles.data.attenuated_backscatter_0.attrs['desaturated'] is True

    def test_foc(self, profiles):
        profiles.foc()
        foc = profiles.data.foc
        # test types
        assert type(foc) is xr.core.dataarray.DataArray

    def test_clouds(self, profiles):
        extrap_profiles = profiles.extrapolate_below(z=150.)
        extrap_profiles.clouds()
        clouds_bases = extrap_profiles.data.clouds_bases
        # test types
        assert type(clouds_bases) is xr.core.dataarray.DataArray
        assert type(clouds_bases.data[0][0]) is np.bool_
    
    def test_pbl(self, profiles):
        extrap_profiles = profiles.extrapolate_below(z=150.)
        extrap_profiles.pbl(under_clouds=False)
        pbl = extrap_profiles.data.pbl
        # test types
        assert type(pbl) is xr.core.dataarray.DataArray
        # test values
        assert np.nanmean(pbl.data) == 1152.3449996566771

    def test_inversion(self, profiles):
        extrap_profiles = profiles.extrapolate_below(z=150.)
        extrap_profiles.inversion(remove_outliers = True)
        ext = extrap_profiles.data.extinction
        aod = extrap_profiles.data.aod
        lr = extrap_profiles.data.lidar_ratio
        # test types
        assert type(ext) is xr.core.dataarray.DataArray
        assert type(aod) is xr.core.dataarray.DataArray
        assert type(lr) is xr.core.dataarray.DataArray
        # test values
        assert np.nanmean(ext.data) == 0.012608274945768006
        assert np.nanmean(aod.data) == 0.07564964967460805
        assert np.nanmean(lr.data) == 50.0

    def test_plot(self, cropped_profiles):
        datetime = np.datetime64('2021-09-09T21:20:00')
        # call plotting functions
        fig1 = cropped_profiles.plot(datetime=datetime, show_fig=False)
        fig2 = cropped_profiles.plot(show_fig=False)
    
    def test_write(self, cropped_profiles):
        # call writing function
        pass