import aprofiles as apro
import pytest
import xarray as xr
import numpy as np


# arrange test
@pytest.fixture
def subaltitude_profiles():
    path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
    profiles = apro.reader.ReadProfiles(path).read()
    # subset altitude to make calculation quicker
    profiles.data = profiles.data.sel(altitude=slice(0, 1000))
    return profiles

@pytest.fixture
def subtime_profiles():
    path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
    profiles = apro.reader.ReadProfiles(path).read()
    # subset time to make calculation quicker
    datetime1 = np.datetime64('2021-09-09T14:00:00')
    datetime2 = np.datetime64('2021-09-09T16:00:00')
    profiles.data = profiles.data.sel(time=slice(datetime1, datetime2))
    return profiles

# test class
class TestProfilesData:
    def test_snr(self, subaltitude_profiles):
        subaltitude_profiles.snr()
        snr = subaltitude_profiles.data.snr
        # test types
        assert type(snr) is xr.core.dataarray.DataArray
        assert type(snr.data) is np.ndarray
        # test values
        #assert np.mean(snr.data) == 8.236267199712106

    def test_gaussian_filter(self, subaltitude_profiles):
        filter = subaltitude_profiles.gaussian_filter(sigma=0.25, var="attenuated_backscatter_0")
        # test attributes
        assert filter.data.attenuated_backscatter_0.attrs['gaussian_filter'] == 0.25
        # test values
        assert np.mean(filter.data.attenuated_backscatter_0.data) == 22.678106250188538

    def test_time_avg(self, subaltitude_profiles):
        avg_profiles = subaltitude_profiles.time_avg(10, var="attenuated_backscatter_0")
        # test attributes
        assert avg_profiles.data.attenuated_backscatter_0.attrs['time averaged (minutes)'] == 10

    def test_extrapolate_below(self, subaltitude_profiles):
        extrap_profiles = subaltitude_profiles.extrapolate_below(var="attenuated_backscatter_0", z=150, method="cst")
        # test attributes
        assert extrap_profiles.data.attenuated_backscatter_0.attrs['extrapolation_low_layers_altitude_agl'] == 150
        assert extrap_profiles.data.attenuated_backscatter_0.attrs['extrapolation_low_layers_method'] == 'cst'
        # test if single value for 5 first indexes
        assert len(np.unique(extrap_profiles.data.attenuated_backscatter_0.data[0][0:5])) == 1

    def test_range_correction(self, subaltitude_profiles):
        range_correc_profiles = subaltitude_profiles.range_correction(var="attenuated_backscatter_0")
        # test attributes
        assert range_correc_profiles.data.attenuated_backscatter_0.attrs['range correction'] is True
        assert range_correc_profiles.data.attenuated_backscatter_0.attrs['units'] is None

    def test_desaturate_below(self, subtime_profiles):
        desaturate_profiles = subtime_profiles.desaturate_below(var="attenuated_backscatter_0", z=4000.)
        # test attributes
        assert desaturate_profiles.data.attenuated_backscatter_0.attrs['desaturated'] is True

    def test_clouds(self, subtime_profiles):
        extrap_profiles = subtime_profiles.extrapolate_below(z=150.)
        extrap_profiles.clouds()
        clouds = extrap_profiles.data.clouds
        # test types
        assert type(clouds) is xr.core.dataarray.DataArray
        assert type(clouds.data[0][0]) is np.bool_

    def test_foc(self, subtime_profiles):
        subtime_profiles.foc()
        foc = subtime_profiles.data.foc
        # test types
        assert type(foc) is xr.core.dataarray.DataArray
    
    def test_pbl(self, subtime_profiles):
        extrap_profiles = subtime_profiles.extrapolate_below(z=150.)
        extrap_profiles.pbl(under_clouds=False)
        pbl = extrap_profiles.data.pbl
        # test types
        assert type(pbl) is xr.core.dataarray.DataArray
        # test values
        assert np.round(np.nanmean(pbl.data),3) == 1532.235

    def test_inversion(self, subtime_profiles):
        extrap_profiles = subtime_profiles.extrapolate_below(z=150.)
        # test forward method
        extrap_profiles.inversion(method="forward", remove_outliers = True)
        ext = extrap_profiles.data.extinction
        aod = extrap_profiles.data.aod
        lr = extrap_profiles.data.lidar_ratio
        # test types
        assert type(ext) is xr.core.dataarray.DataArray
        assert type(aod) is xr.core.dataarray.DataArray
        assert type(lr) is xr.core.dataarray.DataArray
        # test values
        #assert np.round(np.nanmean(ext.data),5) == 0.0165
        #assert np.round(np.nanmean(aod.data),5) == 0.09902
        #assert np.round(np.nanmean(lr.data),3) == 50.0
        # test backward method
        extrap_profiles.inversion(method="backward", remove_outliers = True)
        ext = extrap_profiles.data.extinction
        aod = extrap_profiles.data.aod
        lr = extrap_profiles.data.lidar_ratio
        # test types
        assert type(ext) is xr.core.dataarray.DataArray
        assert type(aod) is xr.core.dataarray.DataArray
        assert type(lr) is xr.core.dataarray.DataArray
        # test values
        #assert np.round(np.nanmean(ext.data),5) == 0.03155
        #assert np.round(np.nanmean(aod.data),5) == 0.17234
        #assert np.round(np.nanmean(lr.data),3) == 50.0

    def test_plot(self, subtime_profiles):
        # data processing
        subtime_profiles.extrapolate_below(z=150, inplace=True)
        subtime_profiles.foc(zmin_cloud=200) 
        subtime_profiles.pbl(zmin=200, zmax=3000, under_clouds=True)
        # call plotting functions
        fig1 = subtime_profiles.plot(show_foc=True, show_clouds=True, show_pbl=True, show_fig=False)
        fig2 = subtime_profiles.plot(datetime=np.datetime64('2021-09-09T21:20:00'), show_foc=True, show_clouds=True, show_pbl=True, show_fig=False)
        fig3 = subtime_profiles.plot(var='calibration_constant_0', show_fig=False)
    
    def test_write(self, subtime_profiles):
        # call writing function
        pass