# @author Augustin Mortier
# @desc A-Profiles - Fog or Condensation detection

from aprofiles import utils


def _detect_fog_from_cloud_base_height(profiles, zmin_cloud):
    # returns a bool list with True where fog/condensation cases
    # if the base of the first cloud (given by the constructor) is below
    first_cloud_base_height = profiles.data.cloud_base_height.data[:, 0]
    # condition
    foc = [True if x <= zmin_cloud else False for x in first_cloud_base_height]
    return foc

def _detect_fog_from_snr(profiles, z_snr, var, min_snr):
    # returns a bool list with True where fog/condensation cases

    # calculates snr at z_snr
    iz_snr = profiles._get_index_from_altitude_AGL(z_snr)
    # calculates snr at each timestamp
    snr = [
        utils.snr_at_iz(profiles.data[var].data[i, :], iz_snr, step=4)
        for i in range(len(profiles.data.time.data))
    ]
    # condition
    foc = [True if x <= min_snr else False for x in snr]
    return foc

def detect_foc(profiles, method="cloud_base", var="attenuated_backscatter_0", z_snr=2000., min_snr=2., zmin_cloud=200.):
    """Detects fog or condensation.

    Args:
        - profiles (:class:`aprofiles.profiles.ProfilesData`): `ProfilesData` instance.
        - method ({'cloud_base', 'snr'}, optional): Defaults to `'cloud_base'`.
        - var (str, optional). Used for 'snr' method. Variable to calculate SNR from. Defaults to `'attenuated_backscatter_0'`.
        - z_snr (float, optional): Used for 'snr' method. Altitude AGL (in m) at which we calculate the SNR. Defaults to `2000.`.
        - min_snr (float, optional): Used for 'snr' method. Minimum SNR under which the profile is considered as containing fog or condensation. Defaults to `2.`.
        - zmin_cloud (float, optional): Used for 'cloud_base' method. Altitude AGL (in m) below which a cloud base height is considered a fog or condensation situation. Defaults to `200.`.

    Returns:
        :class:`aprofiles.profiles.ProfilesData` object with additional :class:`xarray.DataArray` in :attr:`aprofiles.profiles.ProfilesData.data`.
            - `'foc' (time)`: mask array corresponding to the presence of foc.

    Example:
        >>> import aprofiles as apro
        >>> # read example file
        >>> path = "examples/data/L2_0-20000-001492_A20210909.nc"
        >>> reader = apro.reader.ReadProfiles(path)
        >>> profiles = reader.read()
        >>> # foc detection
        >>> profiles.foc()
        >>> # attenuated backscatter image with pbl up to 6km of altitude
        >>> profiles.plot(show_foc=True, zmax=6000., vmin=1e-2, vmax=1e1, log=True)

        .. figure:: ../../examples/images/foc.png
            :scale: 50 %
            :alt: foc detection

            Fog or condensation (foc) detection.
    """

    if method == "cloud_base":
        foc = _detect_fog_from_cloud_base_height(profiles, zmin_cloud)
    elif method.upper() == "SNR":
        foc = _detect_fog_from_snr(profiles, z_snr, var, min_snr)

    # creates dataarray
    profiles.data["foc"] = ("time", foc)
    profiles.data["foc"] = profiles.data.foc.assign_attrs({'long_name': 'Fog or condensation mask'})

    return profiles


def _main():
    import aprofiles as apro

    path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
    profiles = apro.reader.ReadProfiles(path).read()

    # basic corrections
    profiles.extrapolate_below(z=150.0, inplace=True)
    # detection
    profiles.foc().plot(show_foc=True, log=True, vmin=1e-2, vmax=1e1)


if __name__ == "__main__":
    _main()
