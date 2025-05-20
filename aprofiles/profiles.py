# @author Augustin Mortier
# @desc A-Profiles - ProfilesData class

import copy
from pathlib import Path

import numpy as np
import xarray as xr
from rich.progress import track
from typing import Literal

import aprofiles as apro


class ProfilesData:
    """
    Base class representing profiles data returned by (aprofiles.reader.ReadProfiles):.
    """

    def __init__(self, data):
        self.data = data

    @property
    def data(self):
        """
        Data attribute (instance of (xarray.Dataset):)
        """
        return self._data

    @data.setter
    def data(self, data):
        if not isinstance(data, xr.Dataset):
            raise ValueError("Wrong data type: an xarray Dataset is expected.")
        self._data = data

    def _get_index_from_altitude_AGL(self, altitude):
        """
        Returns the closest index of the ProfilesData vertical dimension to a given AGL altitude

        Args:
            altitude (float): in m, altitude AGL to look for

        Returns:
            (int): Closest index of the vertical dimension to the given altitude AGL
        """
        return int(np.argmin(abs(self.data.altitude.data - altitude)))

    def _get_indices_from_altitude_AGL(self, altitude):
        """
        Returns an array of the closest indexes of the ProfilesData vertical dimension to given AGL altitudes

        Args:
            altitudes (array-like): in m, altitudes AGL to look for

        Returns:
            (np.ndarray): Array of closest indices of the vertical dimension to the given altitudes AGL
        """
        altitudes = np.full_like(self.data.station_altitude.data, altitude)
        closest_indices = [
            int(np.argmin(abs(self.data.altitude.data - alt))) for alt in altitudes
        ]
        return closest_indices

    def _get_resolution(self, which):
        """
        Returns the resolution of a given dimension. Supports 'altitude' and 'time'.
        The altitude resolution is given in meters, while the time resolution is given in seconds.

        Args:
            which (str): Dimension: must be ['altitude', 'time'].

        Returns:
            (float): resolution, in m (if which=='altitude') or in s (if which=='time')
        """
        if which == "altitude":
            return min(np.diff(self.data.altitude.data))
        elif which == "time":
            return (
                min(np.diff(self.data.time.data)).astype("timedelta64[s]").astype(int)
            )

    def _get_lowest_clouds(self):
        # returns an array of the altitude (in m, ASL) of the lowest cloud for each timestamp
        lowest_clouds = np.full(np.shape(self.data.time.data), np.nan)
        for i, _ in enumerate(self.data.time.data):
            clouds_profile = self.data.clouds[i, :]
            i_clouds = np.squeeze(np.where(clouds_profile))
            if len(i_clouds) > 0:
                lowest_clouds[i] = self.data.altitude.data[i_clouds[0]]
        return lowest_clouds

    def _get_itime(self, datetime):
        """
        Returns the index of closest datetime available of the ProfilesData object.
        """
        time = self.data.time.data
        i_time = np.argmin(abs(time - datetime))
        return i_time

    def snr(self, var="attenuated_backscatter_0", step=4, verbose=False):
        """
        Method that calculates the Signal to Noise Ratio.

        Args:
            var (str, optional): Variable of the DataArray to calculate the SNR from.
            step (int, optional): Number of steps around we calculate the SNR for a given altitude.
            verbose (bool, optional): Verbose mode.

        Returns:
            (ProfilesData): object with additional (xarray.DataArray): `snr`.

        Example:
            ```python
            import aprofiles as apro
            # read example file
            path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
            reader = apro.reader.ReadProfiles(path)
            profiles = reader.read()
            # snr calculation
            profiles.snr()
            # snr image
            profiles.plot(var='snr',vmin=0, vmax=3, cmap='Greys_r')
            ```
        """

        # Get the dimensions of the data array
        time_len, altitude_len = self.data[var].shape

        # Preallocate the SNR array with zeros
        snr_array = np.zeros((time_len, altitude_len))

        # Loop over each time step
        for t in track(range(time_len), description="snr   ", disable=not verbose):
            # Extract 1D slice for current time step
            array = self.data[var].data[t, :]

            # Create a sliding window view for the rolling calculation
            sliding_windows = np.lib.stride_tricks.sliding_window_view(
                array, window_shape=2 * step + 1, axis=0
            )

            # Calculate mean and std across the window axis
            means = np.nanmean(sliding_windows, axis=1)
            stds = np.nanstd(sliding_windows, axis=1)

            # Handle the edges (where sliding window can't be applied due to boundary)
            means = np.pad(
                means, pad_width=(step,), mode="constant", constant_values=np.nan
            )
            stds = np.pad(
                stds, pad_width=(step,), mode="constant", constant_values=np.nan
            )

            # Avoid division by zero
            stds = np.where(stds == 0, np.nan, stds)

            # Compute SNR
            snr_array[t, :] = np.divide(means, stds, where=(stds != 0))

        # Add the SNR DataArray to the object's data attribute
        self.data["snr"] = (("time", "altitude"), snr_array)
        self.data["snr"] = self.data.snr.assign_attrs(
            {"long_name": "Signal to Noise Ratio", "units": "", "step": step}
        )

        return self

    def gaussian_filter(
        self, sigma=0.25, var="attenuated_backscatter_0", inplace=False
    ):
        """
        Applies a 2D gaussian filter in order to reduce high frequency noise.

        Args:
            sigma (scalar or sequence of scalars, optional): Standard deviation for Gaussian kernel. The standard deviations of the Gaussian filter are given for each axis as a sequence, or as a single number, in which case it is equal for all axes.
            var (str, optional): variable name of the Dataset to be processed.
            inplace (bool, optional): if True, replace the instance of the (ProfilesData): class.

        Returns:
            (ProfilesData): object with additional attributes `gaussian_filter` for the processed (xarray.DataArray):.

        Example:
            ```python
            import aprofiles as apro
            # read example file
            path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
            reader = apro.reader.ReadProfiles(path)
            profiles = reader.read()
            # apply gaussian filtering
            profiles.gaussian_filter(sigma=0.5, inplace=True)
            profiles.data.attenuated_backscatter_0.attrs.gaussian_filter
            0.50
            ```

            ![Before gaussian filtering](../../assets/images/attenuated_backscatter.png)
            ![After gaussian filtering (sigma=0.5)](../../assets/images/gaussian_filter.png)
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
        """
        Rolling median in the time dimension.

        Args:
            minutes (float): Number of minutes to average over.
            var (str, optional): variable of the Dataset to be processed.
            inplace (bool, optional): if True, replace the instance of the (ProfilesData): class.

        Returns:
            (ProfilesData):
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
        """
        Method for extrapolating lowest layers below a certain altitude. This is of particular intrest for instruments subject to After Pulse effect, with saturated signal in the lowest layers.
        We recommend to use a value of zmin=150m due to random values often found below that altitude which perturbs the clouds detection.

        Args:
            var (str, optional): variable of the :class:`xarray.Dataset` to be processed.
            z (float, optional): Altitude (in m, AGL) below which the signal is extrapolated.
            method ({'cst', 'lin'}, optional): Method to be used for extrapolation of lowest layers.
            inplace (bool, optional): if True, replace the instance of the (ProfilesData): class.

        Returns:
            (ProfilesData): object with additional attributes:

                - `extrapolation_low_layers_altitude_agl`
                - `extrapolation_low_layers_method` for the processed (xarray.DataArray):.

        Example:
            ```python
            import aprofiles as apro
            # read example file
            path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
            reader = apro.reader.ReadProfiles(path)
            profiles = reader.read()
            # desaturation below 4000m
            profiles.extrapolate_below(z=150., inplace=True)
            profiles.data.attenuated_backscatter_0.extrapolation_low_layers_altitude_agl
            150
            ```

            ![Before extrapolation](../../assets/images/lowest.png)
            ![After extrapolation](../../assets/images/lowest_extrap.png)
        """

        # get index of z
        imax = self._get_indices_from_altitude_AGL(z)
        nt = np.shape(self.data[var].data)[0]

        if method == "cst":
            # get values at imax indices
            data_zmax = np.array([self.data[var].data[t, imax[t]] for t in range(nt)])

            # replace values
            filling_matrice = np.array(
                [np.full(max(imax), data_zmax[t]) for t in range(nt)]
            )
        elif method == "lin":
            raise NotImplementedError("Linear extrapolation is not implemented yet")
        else:
            raise ValueError("Expected string: lin or cst")

        if inplace:
            for t in range(nt):
                self.data[var].data[t, : imax[t]] = filling_matrice[t, : imax[t]]
            new_profiles_data = self
            filling_matrice[t, : imax[t]]
        else:
            copied_dataset = copy.deepcopy(self)
            for t in range(nt):
                copied_dataset.data[var].data[t, : imax[t]] = filling_matrice[
                    t, : imax[t]
                ]
            new_profiles_data = copied_dataset

        # add attributes
        new_profiles_data.data[var].attrs["extrapolation_low_layers_altitude_agl"] = z
        new_profiles_data.data[var].attrs["extrapolation_low_layers_method"] = method

        return new_profiles_data

    def range_correction(self, var="attenuated_backscatter_0", inplace=False):
        """
        Method that corrects the solid angle effect (1/z2) which makes that the backscatter beam is more unlikely to be detected with the square of the altitude.

        Args:
            var (str, optional): variable of the Dataset to be processed.
            inplace (bool, optional): if True, replace the instance of the (ProfilesData): class.

        Returns:
            (ProfilesData):

        .. warning::
            Make sure that the range correction is not already applied to the selected variable.
        """

        range_corrected_data = []

        for i in range(len(self.data.time.data)):
            # for the altitude correction, must one use the altitude above the ground level
            z_agl = self.data.altitude.data - self.data.station_altitude.data[i]

            data = self.data[var].data[i, :]
            range_corrected_data.append(np.multiply(data, z_agl))

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
        """
        Remove saturation caused by clouds at low altitude which results in negative values above the maximum.
        The absolute value of the signal is returned below the prescribed altitude.

        Args:
            var (str, optional): variable of the :class:`xarray.Dataset` to be processed.
            z (float, optional): Altitude (in m, AGL) below which the signal is unsaturated.
            inplace (bool, optional): if True, replace the instance of the (ProfilesData):.

        Todo:
            Refine method to desaturate only saturated areas.

        Returns:
            (ProfilesData): object with additional attribute `desaturate` for the processed (xarray.DataArray):.

        .. warning::
            For now, absolute values are returned everywhere below the prescribed altitude.

        Example:
            ```python
            import aprofiles as apro
            # read example file
            path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
            reader = apro.reader.ReadProfiles(path)
            profiles = reader.read()
            # desaturation below 4000m
            profiles.desaturate_below(z=4000., inplace=True)
            profiles.data.attenuated_backscatter_0.desaturated
            True
            ```

            ![Before desaturation](../../assets/images/saturated.png)
            ![After desaturation](../../assets/images/desaturated.png)
        """

        imax = self._get_indices_from_altitude_AGL(z)
        unsaturated_data = copy.deepcopy(self.data[var].data)
        for i in range(len(self.data.time.data)):
            unsaturated_data[i, : imax[i]] = abs(unsaturated_data[i, : imax[i]])

        if inplace:
            self.data[var].data = unsaturated_data
            new_profiles_data = self
        else:
            copied_dataset = copy.deepcopy(self)
            copied_dataset.data[var].data = unsaturated_data
            new_profiles_data = copied_dataset

        # add attribute
        new_profiles_data.data[var].attrs["desaturated"] = str(True)
        return new_profiles_data

    def foc(
        self,
        method="cloud_base",
        var="attenuated_backscatter_0",
        z_snr=2000.0,
        min_snr=2.0,
        zmin_cloud=200.0,
    ):
        """
        Calls :meth:`aprofiles.detection.foc.detect_foc()`.
        """
        return apro.detection.foc.detect_foc(
            self, method, var, z_snr, min_snr, zmin_cloud
        )

    def clouds(
        self,
        method: Literal["dec", "vg"] = "dec",
        time_avg=1,
        zmin=0,
        thr_noise=5.0,
        thr_clouds=4.0,
        min_snr=0.0,
        verbose=False,
    ):
        """
        Calls :meth:`aprofiles.detection.clouds.detect_clouds()`.
        """
        return apro.detection.clouds.detect_clouds(
            self, method, time_avg, zmin, thr_noise, thr_clouds, min_snr, verbose
        )

    def pbl(
        self,
        time_avg=1,
        zmin=100.0,
        zmax=3000.0,
        wav_width=200.0,
        under_clouds=True,
        min_snr=2.0,
        verbose=False,
    ):
        """
        Calls :meth:`aprofiles.detection.pbl.detect_pbl()`.
        """
        return apro.detection.pbl.detect_pbl(
            self, time_avg, zmin, zmax, wav_width, under_clouds, min_snr, verbose
        )

    def inversion(
        self,
        time_avg=1,
        zmin=4000.0,
        zmax=6000.0,
        min_snr=0.0,
        under_clouds=False,
        method="forward",
        apriori={"lr": 50.0, "mec": False, "use_cfg": False},
        remove_outliers=False,
        mass_conc=True,
        mass_conc_method="mortier_2013",
        verbose=False,
    ):
        """
        Calls :meth:`aprofiles.retrieval.extinction.inversion()` to calculate extinction profiles.
        Calls :meth:`aprofiles.retrieval.mass_conc.mec()` to calculate Mass to Extinction coefficients if `mass_conc` is true (Default).
        """
        apro.retrieval.extinction.inversion(
            self,
            time_avg,
            zmin,
            zmax,
            min_snr,
            under_clouds,
            method,
            apriori,
            remove_outliers,
            verbose,
        )
        if mass_conc:
            apro.retrieval.mass_conc.concentration_profiles(
                self, mass_conc_method, apriori
            )
        return apro

    def plot(
        self,
        var="attenuated_backscatter_0",
        datetime=None,
        zref="agl",
        zmin=None,
        zmax=None,
        vmin=None,
        vmax=None,
        log=False,
        show_foc=False,
        show_pbl=False,
        show_clouds=False,
        cmap="coolwarm",
        show_fig=True,
        save_fig=None,
        **kwargs
    ):
        """
        Plotting method.
        Depending on the variable selected, this method will plot an image, a single profile or a time series of the requested variable.
        See also :ref:`Plotting`.

        Args:
            var (str, optional): Variable to be plotted.
            datetime (:class:`numpy.datetime64`, optional): if provided, plot the profile for closest time. If not, plot an image constructed on all profiles.
            zref ({'agl', 'asl'}, optional): Base reference for the altitude axis.
            zmin (float, optional): Minimum altitude AGL (m).
            zmax (float, optional): Maximum altitude AGL (m).
            vmin (float, optional): Minimum value.
            vmax (float, optional): Maximum value.
            log (bool, optional): Use logarithmic scale.
            show_foc (bool, optional): Show fog or condensation retrievals.
            show_pbl (bool, optional): Show PBL height retrievals.
            show_clouds (bool, optional): Show clouds retrievals.
            cmap (str, optional): Matplotlib colormap.
            show_fig (bool, optional): Show Figure.
            save_fig (str, optional): Path of the saved figure.
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
                apro.plot.image.plot(
                    self.data,
                    var,
                    zref,
                    zmin,
                    zmax,
                    vmin,
                    vmax,
                    log,
                    show_foc,
                    show_pbl,
                    show_clouds,
                    cmap,
                    show_fig,
                    save_fig,
                )
            else:
                apro.plot.timeseries.plot(self.data, var, show_fig, save_fig, **kwargs)
        else:
            apro.plot.profile.plot(
                self.data,
                datetime,
                var,
                zref,
                zmin,
                zmax,
                vmin,
                vmax,
                log,
                show_foc,
                show_pbl,
                show_clouds,
                show_fig,
                save_fig,
            )

    def write(self, base_dir=Path("examples", "data", "V-Profiles"), verbose=False):
        """
        Calls :meth:`aprofiles.io.write_profiles.write()`.
        """
        apro.io.write_profiles.write(self, base_dir, verbose=verbose)


def _main():
    import aprofiles as apro

    path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
    profiles = apro.reader.ReadProfiles(path).read()

    # basic corrections
    profiles.extrapolate_below(z=150.0, inplace=True)
    profiles.desaturate_below(z=4000.0, inplace=True)

    # detection
    profiles.foc(method="cloud_base", zmin_cloud=200)
    profiles.clouds(zmin=300, thr_noise=5, thr_clouds=4, verbose=True)
    profiles.pbl()
    # profiles.plot(show_foc=True, show_clouds=True, log=True, vmin=1e-2, vmax=1e1)

    # inversion
    profiles.inversion(
        zmin=4000.0,
        zmax=6000.0,
        method="forward",
        apriori={"lr": 50.0},
        mass_conc=True,
        verbose=True,
    )

    # write results
    profiles.write()


if __name__ == "__main__":
    _main()
