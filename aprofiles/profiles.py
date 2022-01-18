# @author Augustin Mortier
# @desc A-Profiles - ProfilesData class

import copy

import numpy as np
import xarray as xr
from tqdm import tqdm

import aprofiles as apro


class ProfilesData:
    """Base class representing profiles data returned by :class:`aprofiles.reader.ReadProfiles`."""

    def __init__(self, data):
        self.data = data

    @property
    def data(self):
        """Data attribute (instance of :class:`xarray.Dataset`)"""
        return self._data

    @data.setter
    def data(self, data):
        if not isinstance(data, xr.Dataset):
            raise ValueError("Wrong data type: an xarray Dataset is expected.")
        self._data = data

    def _get_index_from_altitude_AGL(self, altitude):
        """Returns the closest index of the ProfilesData vertical dimension to a given AGL altitude

        Args:
            altitude (float): in m, altitude AGL to look for

        Returns:
            int: Closest index of the vertical dimension to the given altitude AGL
        """
        altitude_asl = altitude + self.data.station_altitude.data
        return int(np.argmin(abs(self.data.altitude.data - altitude_asl)))

    def _get_resolution(self, which):
        """Returns the resolution of a given dimension. Support 'altitude' and 'time'.
        The altitude resolution is given in meters, while the time resolution is given in seconds.

        Args:
            which ({'altitude','time'}): Defaults to `'altitude'`.

        Returns:
            float: resolution, in m (if which=='altitude') or in s (if which=='time')
        """
        if which == "altitude":
            return min(np.diff(self.data.altitude.data))
        elif which == "time":
            return (
                min(np.diff(self.data.time.data)).astype("timedelta64[s]").astype(int)
            )

    def _get_lowest_clouds(self):
        # returns an array of the altitude (in m, ASL) of the lowest cloud for each timestamp

        def get_true_indexes(mask):
            # mask: list of Bool
            # returns a list indexes where the mask is True
            return [i for i, x in enumerate(mask) if x]

        lowest_clouds = []
        for i in np.arange(len(self.data.time.data)):
            i_clouds = get_true_indexes(self.data.clouds_bases.data[i, :])
            if len(i_clouds) > 0:
                lowest_clouds.append(self.data.altitude.data[i_clouds[0]])
            else:
                lowest_clouds.append(np.nan)

        return lowest_clouds

    def _get_itime(self, datetime):
        """Returns the index of closest datetime available of the ProfilesData object."""
        time = self.data.time.data
        i_time = np.argmin(abs(time - datetime))
        return i_time

    def snr(self, var="attenuated_backscatter_0", step=4, verbose=False):
        """Method that calculates the Signal to Noise Ratio.

        Args:
            - var (str, optional): Variable of the DataArray to calculate the SNR from. Defaults to `'attenuated_backscatter_0'`.
            - step (int, optional): Number of steps around we calculate the SNR for a given altitude. Defaults to `4`.
            - verbose (bool, optional): Verbose mode. Defaults to `False`.

        Returns:
            :class: :class:`ProfilesData` object with additional :class:`xarray.DataArray` `snr`.

        .. note::
            This calculation is relatively heavy in terms of calculation.

        Example:
            >>> import aprofiles as apro
            >>> # read example file
            >>> path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
            >>> reader = apro.reader.ReadProfiles(path)
            >>> profiles = reader.read()
            >>> # snr calculcation
            >>> profiles.snr()
            >>> # snr image
            >>> profiles.plot(var='snr',vmin=0, vmax=3, cmap='Greys_r')

            .. figure:: ../../docs/_static/images/snr.png
                :scale: 50 %
                :alt: snr

                Signal to Noise Ratio.
        """

        def _1D_snr(array, step):
            array = np.asarray(array)
            snr = []
            for i in np.arange(len(array)):
                gates = np.arange(i - step, i + step)
                indexes = [i for i in gates if i > 0 and i < len(array)]
                mean = np.nanmean(array[indexes])
                std = np.nanstd(array[indexes])
                if std != 0:
                    snr.append(mean / std)
                else:
                    snr.append(0)
            return np.asarray(snr)

        snr = []

        for i in (
            tqdm(range(len(self.data.time.data)), desc="snr   ")
            if verbose
            else range(len(self.data.time.data))
        ):
            snr.append(_1D_snr(self.data[var].data[i, :], step))

        # creates dataarrays
        self.data["snr"] = (('time', 'altitude'), np.asarray(snr))
        self.data["snr"] = self.data.snr.assign_attrs({
            'long_name': 'Signal to Noise Ratio',
            'units': '',
            'step': step
        })

        return self

    def gaussian_filter(
        self, sigma=0.25, var="attenuated_backscatter_0", inplace=False
    ):
        """Applies a 2D gaussian filter in order to reduce high frequency noise.

        Args:
            - sigma (scalar or sequence of scalars, optional): Standard deviation for Gaussian kernel. The standard deviations of the Gaussian filter are given for each axis as a sequence, or as a single number, in which case it is equal for all axes. Defaults to `0.25`.
            - var (str, optional): variable name of the Dataset to be processed. Defaults to `'attenuated_backscatter_0'`.
            - inplace (bool, optional): if True, replace the instance of the :class:`ProfilesData` class. Defaults to `False`.

        Returns:
            :class:`ProfilesData` object with additional attributes `gaussian_filter` for the processed :class:`xarray.DataArray`.

        Example:
            >>> import aprofiles as apro
            >>> # read example file
            >>> path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
            >>> reader = apro.reader.ReadProfiles(path)
            >>> profiles = reader.read()
            >>> # apply gaussian filtering
            >>> profiles.gaussian_filter(sigma=0.5, inplace=True)
            >>> profiles.data.attenuated_backscatter_0.attrs.gaussian_filter
            0.50

            .. figure:: ../../docs/_static/images/attenuated_backscatter.png
                :scale: 50 %
                :alt: before filtering

                Before gaussian filtering.

            .. figure:: ../../docs/_static/images/gaussian_filter.png
                :scale: 50 %
                :alt: after gaussian filtering

                After gaussian filtering (sigma=0.5).
        """
        import copy

        from scipy.ndimage import gaussian_filter

        # apply gaussian filter
        filtered_data = gaussian_filter(self.data[var].data, sigma=sigma)

        if inplace:
            self.data[var].data = filtered_data
            new_dataset = self
        else:
            copied_dataset = copy.deepcopy(self)
            copied_dataset.data[var].data = filtered_data
            new_dataset = copied_dataset
        # add attribute
        new_dataset.data[var].attrs["gaussian_filter"] = sigma
        return new_dataset

    def time_avg(self, minutes, var="attenuated_backscatter_0", inplace=False):
        """Rolling median in the time dimension.

        Args:
            - minutes (float): Number of minutes to average over.
            - var (str, optional): variable of the Dataset to be processed. Defaults to `'attenuated_backscatter_0'`.
            - inplace (bool, optional): if True, replace the instance of the :class:`ProfilesData` class. Defaults to `False`.

        Returns:
            :class: :class:`ProfilesData` object.
        """
        rcs = self.data[var].copy()
        # time conversion from minutes to seconds
        t_avg = minutes * 60
        # time resolution in profiles data in seconds
        dt_s = self._get_resolution("time")
        # number of timestamps to be to averaged
        nt_avg = max([1, round(t_avg / dt_s)])
        # rolling median
        filtered_data = (
            rcs.rolling(time=nt_avg, min_periods=1, center=True).median().data
        )

        if inplace:
            self.data[var].data = filtered_data
            new_dataset = self
        else:
            copied_dataset = copy.deepcopy(self)
            copied_dataset.data[var].data = filtered_data
            new_dataset = copied_dataset
        # add attribute
        new_dataset.data[var].attrs["time averaged (minutes)"] = minutes
        return new_dataset

    def extrapolate_below(
        self, var="attenuated_backscatter_0", z=150, method="cst", inplace=False
    ):
        """Method for extrapolating lowest layers below a certain altitude. This is of particular intrest for instruments subject to After Pulse effect, with saturated signal in the lowest layers.
        We recommend to use a value of zmin=150m due to random values often found below that altitude which perturbs the clouds detection.

        Args:
            - var (str, optional): variable of the :class:`xarray.Dataset` to be processed. Defaults to `'attenuated_backscatter_0'`.
            - z (float, optional): Altitude (in m, AGL) below which the signal is extrapolated. Defaults to `150`.
            - method ({'cst', 'lin'}, optional): Method to be used for extrapolation of lowest layers. Defaults to `'cst'`.
            - inplace (bool, optional): if True, replace the instance of the :class:`ProfilesData` class. Defaults to `False`.

        Returns:
            :class:`ProfilesData` object with additional attributes `extrapolation_low_layers_altitude_agl` and `extrapolation_low_layers_method` for the processed :class:`xarray.DataArray`.

        Example:
            >>> import aprofiles as apro
            >>> # read example file
            >>> path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
            >>> reader = apro.reader.ReadProfiles(path)
            >>> profiles = reader.read()
            >>> # desaturation below 4000m
            >>> profiles.extrapolate_below(z=150., inplace=True)
            >>> profiles.data.attenuated_backscatter_0.extrapolation_low_layers_altitude_agl
            150

            .. figure:: ../../docs/_static/images/lowest.png
                :scale: 50 %
                :alt: before extrapolation

                Before extrapolation.

            .. figure:: ../../docs/_static/images/lowest_extrap.png
                :scale: 50 %
                :alt: after desaturation

                After extrapolation.
        """

        # get index of z
        imax = self._get_index_from_altitude_AGL(z)

        nt = np.shape(self.data[var].data)[0]

        if method == "cst":
            # get values at imin
            data_zmax = self.data[var].data[:, imax]
            # generates ones matrice with time/altitude dimension to fill up bottom
            ones = np.ones((nt, imax))
            # replace values
            filling_matrice = np.transpose(np.multiply(np.transpose(ones), data_zmax))
        elif method == "lin":
            raise NotImplementedError("Linear extrapolation is not implemented yet")
        else:
            raise ValueError("Expected string: lin or cst")

        if inplace:
            self.data[var].data[:, 0:imax] = filling_matrice
            new_profiles_data = self
        else:
            copied_dataset = copy.deepcopy(self)
            copied_dataset.data[var].data[:, 0:imax] = filling_matrice
            new_profiles_data = copied_dataset

        # add attributes
        new_profiles_data.data[var].attrs["extrapolation_low_layers_altitude_agl"] = z
        new_profiles_data.data[var].attrs["extrapolation_low_layers_method"] = method
        return new_profiles_data

    def range_correction(self, var="attenuated_backscatter_0", inplace=False):
        """Method that corrects the solid angle effect (1/z2) which makes that the backscatter beam is more unlikely to be detected with the square of the altitude.

        Args:
            - var (str, optional): variable of the Dataset to be processed. Defaults to `'attenuated_backscatter_0'`.
            - inplace (bool, optional): if True, replace the instance of the :class:`ProfilesData` class. Defaults to `False`.

        Returns:
            :class: :class:`ProfilesData` object.

        .. warning::
            Make sure that the range correction is not already applied to the selected variable.
        """

        # for the altitude correction, must one use the altitude above the ground level
        z_agl = self.data.altitude.data - self.data.station_altitude.data

        data = self.data[var].data
        range_corrected_data = np.multiply(data, z_agl)

        if inplace:
            self.data[var].data = range_corrected_data
            new_profiles_data = self
        else:
            copied_dataset = copy.deepcopy(self)
            copied_dataset.data[var].data = range_corrected_data
            new_profiles_data = copied_dataset

        # add attribute
        new_profiles_data.data[var].attrs["range correction"] = True
        # remove units
        new_profiles_data.data[var].attrs["units"] = None
        return new_profiles_data

    def desaturate_below(self, var="attenuated_backscatter_0", z=4000.0, inplace=False):
        """Remove saturation caused by clouds at low altitude which results in negative values above the maximum.
        The absolute value of the signal is returned below the prescribed altitude.

        Args:
            - var (str, optional): variable of the :class:`xarray.Dataset` to be processed. Defaults to `'attenuated_backscatter_0'`.
            - z (float, optional): Altitude (in m, AGL) below which the signal is unsaturated. Defaults to `4000.`.
            - inplace (bool, optional): if True, replace the instance of the :class:`ProfilesData` class. Defaults to `False`.

        Todo:
            Refine method to desaturate only saturated areas.

        Returns:
            :class:`ProfilesData` object with additional attribute `desaturate` for the processed :class:`xarray.DataArray`.

        .. warning::
            For now, absolute values are returned everywhere below the prescribed altitude.

        Example:
            >>> import aprofiles as apro
            >>> # read example file
            >>> path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
            >>> reader = apro.reader.ReadProfiles(path)
            >>> profiles = reader.read()
            >>> # desaturation below 4000m
            >>> profiles.desaturate_below(z=4000., inplace=True)
            >>> profiles.data.attenuated_backscatter_0.desaturated
            True

            .. figure:: ../../docs/_static/images/saturated.png
                :scale: 50 %
                :alt: before desaturation

                Before desaturation.

            .. figure:: ../../docs/_static/images/desaturated.png
                :scale: 50 %
                :alt: after desaturation

                After desaturation.
        """

        imax = self._get_index_from_altitude_AGL(z)
        unsaturated_data = copy.deepcopy(self.data[var].data)
        for i in range(len(self.data.time.data)):
            unsaturated_data[i, :imax] = abs(unsaturated_data[i, :imax])

        if inplace:
            self.data[var].data = unsaturated_data
            new_profiles_data = self
        else:
            copied_dataset = copy.deepcopy(self)
            copied_dataset.data[var].data = unsaturated_data
            new_profiles_data = copied_dataset

        # add attribute
        new_profiles_data.data[var].attrs["desaturated"] = "True"
        return new_profiles_data

    def foc(self, method="cloud_base", var="attenuated_backscatter_0", z_snr=2000., min_snr=2., zmin_cloud=200.):
        """Calls :meth:`aprofiles.detection.foc.detect_foc()`."""
        return apro.detection.foc.detect_foc(self, method, var, z_snr, min_snr, zmin_cloud)

    def clouds(self, time_avg=1, zmin=0, thr_noise=5., thr_clouds=4., min_snr=0.0, verbose=False):
        """Calls :meth:`aprofiles.detection.clouds.detect_clouds()`."""
        return apro.detection.clouds.detect_clouds(self, time_avg, zmin, thr_noise, thr_clouds, min_snr, verbose)

    def pbl(self, time_avg=1, zmin=100., zmax=3000., wav_width=200., under_clouds=True, min_snr=2., verbose=False):
        """Calls :meth:`aprofiles.detection.pbl.detect_pbl()`."""
        return apro.detection.pbl.detect_pbl(self, time_avg, zmin, zmax, wav_width, under_clouds, min_snr, verbose)

    def inversion(self, time_avg=1, zmin=4000., zmax=6000., min_snr=0., under_clouds=False, method="forward", 
        apriori={"lr": 50.}, remove_outliers=False, mass_conc=True, mass_conc_method="mortier_2013", verbose=False,
    ):
        """Calls :meth:`aprofiles.retrieval.extinction.inversion()` to calculate extinction profiles.
        Calls :meth:`aprofiles.retrieval.mass_conc.mec()` to calculate Mass to Extinction coefficients if `mass_conc` is true (Default).
        """
        apro.retrieval.extinction.inversion(self, time_avg, zmin, zmax, min_snr, under_clouds, method, apriori, remove_outliers, verbose)
        if mass_conc:
            apro.retrieval.mass_conc.concentration_profiles(self, mass_conc_method)
        return apro

    def plot(
        self, var="attenuated_backscatter_0", datetime=None, zref="agl", zmin=None, zmax=None, vmin=None, vmax=None, log=False,
        show_foc=False, show_pbl=False, show_clouds=False, cmap="coolwarm", show_fig=True, save_fig=None, **kwargs
    ):
        """Plotting method.
        Depending on the variable selected, this method will plot an image, a single profile or a time series of the requested variable.
        See also :ref:`Plotting`.

        Args:
            - var (str, optional): Variable to be plotted. Defaults to `'attenuated_backscatter_0'`.
            - datetime (:class:`numpy.datetime64`, optional): if provided, plot the profile for closest time. If not, plot an image constructed on all profiles.Defaults to `None`.
            - zref ({'agl', 'asl'}, optional): Base reference for the altitude axis.. Defaults to `'agl'`
            - zmin (float, optional): Minimum altitude AGL (m). Defaults to `None`. If `None`, sets to minimum available altitude.
            - zmax (float, optional): Maximum altitude AGL (m). Defaults to `None`. If `None`, sets maximum available altitude.
            - vmin (float, optional): Minimum value. Defaults to `None`.
            - vmax (float, optional): Maximum value. Defaults to `None`. If `None`, calculates max from data.
            - log (bool, optional), Use logarithmic scale. Defaults to `False`.
            - show_foc (bool, optional): Show fog or condensation retrievals. Defaults to `False`.
            - show_pbl (bool, optional): Show PBL height retrievals. Defaults to `False`.
            - show_clouds (bool, optional): Show clouds retrievals. Defaults to `False`.
            - cmap (str, optional): Matplotlib colormap. Defaults to `'coolwarm'`.
            - show_fig (bool, optional): Show Figure. Defaults to `True`.
            - save_fig (str, optional): Path of the saved figure. Defaults to `None`.
        """

        # check if var is available
        if var not in list(self.data.data_vars):
            raise ValueError(
                "{} is not a valid variable. \n List of available variables: {}".format(
                    var, list(self.data.data_vars)
                )
            )

        # here, check the dimension. If the variable has only the time dimension, calls timeseries method
        if datetime is None:
            # check dimension of var
            if len(list(self.data[var].dims)) == 2:
                apro.plot.image.plot(self.data, var, zref, zmin, zmax, vmin, vmax, log, show_foc, show_pbl, show_clouds, cmap, show_fig, save_fig)
            else:
                apro.plot.timeseries.plot(self.data, var, show_fig, save_fig, **kwargs)
        else:
            apro.plot.profile.plot(self.data, datetime, var, zref, zmin, zmax, vmin, vmax, log, show_foc, show_pbl, show_clouds, show_fig, save_fig)
    
    def write(self, base_dir='examples/data/V-Profiles/', verbose=False):
        """Calls :meth:`aprofiles.io.write_profiles.write()`."""
        apro.io.write_profiles.write(self, base_dir, verbose=verbose)
        


def _main():
    import aprofiles as apro

    path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
    profiles = apro.reader.ReadProfiles(path).read()

    # basic corrections
    profiles.extrapolate_below(z=150., inplace=True)
    profiles.desaturate_below(z=4000., inplace=True)
    
    # detection
    profiles.foc(method="cloud_base", zmin_cloud=200)
    profiles.clouds(zmin=300, thr_noise=5, thr_clouds=4, verbose=True)
    profiles.pbl()
    #profiles.plot(show_foc=True, show_clouds=True, log=True, vmin=1e-2, vmax=1e1)
    
    # inversion
    profiles.inversion(zmin=4000., zmax=6000., method="forward", apriori={"lr":50.},mass_conc=True, verbose=True)
    
    # write results
    profiles.write()

if __name__ == "__main__":
    _main()
