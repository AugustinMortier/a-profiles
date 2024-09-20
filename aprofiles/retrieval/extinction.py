# @author Augustin Mortier
# @desc A-Profiles - Aerosol Inversion

import warnings

import numpy as np
from rich.progress import track

import aprofiles as apro

from .ref_altitude import get_iref


def backward_inversion(data, iref, apriori, rayleigh):
    """Backward (Klett [#]_ ) inversion method.

    .. [#] Klett, J. D. (1985). Lidar inversion with variable backscatter/extinction ratios. Applied optics, 24(11), 1638-1643.

    Args:
        - data (array_like): 1D Array of single profile of attenuated backscatter coefficient.
        - iref (float): index of the reference altitude returned by :func:`aprofiles.retrieval.ref_altitude.get_iref()`.
        - apriori (dict): A priori value to be used to constrain the inversion. Valid keys: ‘lr’ (Lidar Ratio, in sr) and ‘aod’ (unitless).
        - rayleigh (:class:`aprofiles.rayleigh.RayleighData`). Instance of the :class:`aprofiles.rayleigh.RayleighData` class.

    Raises:
        NotImplementedError: AOD apriori is not implemented yet.

    Returns:
        array_like: Extinction coefficient, in m-1.
    """

    if "aod" in apriori:
        # search by dichotomy the LR that matches the apriori aod
        raise NotImplementedError("AOD apriori is not implemented yet")
        lr_aer = 50
    else:
        # if we assume the LR, no need to minimize for matching aod
        lr_aer = apriori["lr"]
    lr_mol = 8.0 * np.pi / 3.0

    # vertical resolution
    dz = min(np.diff(rayleigh.altitude))

    int1_a = np.cumsum((lr_aer - lr_mol) * rayleigh.backscatter[:iref] * dz)
    int1_b = [2 * int1_a[-1] - 2 * int1_a[i] for i in range(iref)]
    phi = [np.log(abs(data[i] / data[iref])) + int1_b[i] for i in range(iref)]

    int2_a = 2 * np.nancumsum(lr_aer * np.exp(phi) * dz)
    int2_b = [int2_a[-1] - int2_a[i] for i in range(iref)]

    # initialize total backscatter
    back_aer_iref = 0  # m-1
    beta_tot_iref = rayleigh.backscatter[iref] + back_aer_iref

    # total backscatter
    beta_tot = [np.exp(phi[i]) / ((1 / beta_tot_iref) + int2_b[i]) for i in range(iref)]
    # aerosol backsatter (m-1.sr-1)
    beta_aer = beta_tot - rayleigh.backscatter[:iref]
    # aerosol extinction (m-1)
    sigma_aer = lr_aer * beta_aer
    # returns extinction in m-1 when valid, and np.nan elsewhere
    ext = [sigma_aer[i] if i < len(sigma_aer) else np.nan for i in range(len(data))]
    return ext


def forward_inversion(data, iref, apriori, rayleigh):
    """Forward iterative inversion method [#]_.

    .. [#] Li, D., Wu, Y., Gross, B., & Moshary, F. (2021). Capabilities of an Automatic Lidar Ceilometer to Retrieve Aerosol Characteristics within the Planetary Boundary Layer. Remote Sensing, 13(18), 3626.

    Method principle:

    At z0, the aerosol transmission is assumed as being close to 1. We evaluate the aerosol extinction based on this assumption.
    This evaluation gives a refined aerosol extinction that is used to calculate a second time the aerosol transmission.
    The aerosol extinction retrieval will converge after a certain number iterations.
    After the convergence, the aerosol extinction is retrieved in the next upper layer.

    Args:
        - data (array_like): 1D Array of single profile of attenuated backscatter coefficient, in m-1.sr-1.
        - iref (float): index of the reference altitude returned by :func:`aprofiles.retrieval.ref_altitude.get_iref()`.
        - apriori (dict): A priori value to be used to constrain the inversion. Valid keys: ‘lr’ (Lidar Ratio, in sr) and ‘aod’ (unitless).
        - rayleigh (:class:`aprofiles.rayleigh.RayleighData`). Instance of the :class:`aprofiles.rayleigh.RayleighData` class.

    Raises:
        NotImplementedError: AOD apriori is not implemented yet.

    Returns:
        array_like: Extinction coefficient, in m-1.
    """

    if "aod" in apriori:
        # search by dichotomy the LR that matches the apriori aod
        raise NotImplementedError("AOD apriori is not implemented yet")
        lr_aer = 50
    else:
        # if we assume the LR, no need to minimize for matching aod
        lr_aer = apriori["lr"]
    lr_mol = 8.0 * np.pi / 3.0

    def _get_aer_at_i(data, i, Tm, Bm, Ta, Ba, Ea, dz, nloop_max=30, diff_ext=0.01):
        # suppress warnings
        warnings.filterwarnings('ignore')

        for _ in range(nloop_max):
            if np.isnan(Ea[i]):
                Ta[i] = 1
            else:
                Ta[i] = np.exp(-np.nancumsum(Ea * dz))[i]
            if (Tm[i] ** 2 * Ta[i] ** 2) != 0:
                Ba[i] = data[i] / (Tm[i] ** 2 * Ta[i] ** 2) - Bm[i]
            else:
                Ba[i] = np.nan
            # test extinction
            if 1 - (lr_aer * Ba[i] / Ea[i]) < diff_ext:
                Ea[i] = lr_aer * Ba[i]
                break
            Ea[i] = lr_aer * Ba[i]

        return Ba[i], Ea[i], Ta[i]

    # vertical resolution
    dz = min(np.diff(rayleigh.altitude))

    Bm = rayleigh.backscatter
    Em = rayleigh.extinction
    Tm = np.exp(-np.cumsum(Em * dz))

    # Initialize aer profiles
    Ta = np.asarray([np.nan for _ in range(len(data))])
    Ba = np.asarray([np.nan for _ in range(len(data))])
    Ea = np.asarray([np.nan for _ in range(len(data))])

    for i in range(iref):
        Ba[i], Ea[i], Ta[i] = _get_aer_at_i(data, i, Tm, Bm, Ta, Ba, Ea, dz)
        if np.isnan(Ba[i]):
            continue
    # returns extinction in m-1
    ext = Ea
    return ext


def inversion(
    profiles,
    time_avg=1,
    zmin=4000.0,
    zmax=6000.0,
    min_snr=0.0,
    under_clouds=False,
    method="forward",
    apriori={"lr": 50.0},
    remove_outliers=False,
    verbose=False,
):
    """Aerosol inversion of the attenuated backscatter profiles using an apriori.

    Args:
        - profiles (:class:`aprofiles.profiles.ProfilesData`): `ProfilesData` instance.
        - time_avg (int, optional): in minutes, the time during which we aggregate the profiles before inverting the profiles. Defaults to 1.
        - zmin (float, optional): minimum altitude AGL, in m, for looking for the initialization altitude. Defaults to 4000..
        - zmax (float, optional): maximum altitude AGL, in m, for looking for the initialization altitude. Defaults to 6000..
        - min_snr (float, optional). Minimum SNR required at the reference altitude to be valid. Defaults to 0.
        - under_clouds (bool, optional): If True, and if the `ProfilesData` has a `cloud_base` variable (returned by the `clouds` method), forces the initialization altitude to be found below the first cloud detected in the profile. Defaults to True.
        - method ({‘backward’, ‘forward’}, optional). Defaults to ‘forward’.
        - apriori (dict, optional). A priori value to be used to constrain the inversion. Valid keys: ‘lr’ (Lidar Ratio, in sr) and ‘aod’ (unitless). Defaults to {‘lr’: 50}.
        - remove_outliers (bool, optional). Remove profiles considered as outliers based on aod calculation (AOD<0, or AOD>2). Defaults to False (while development. to be changed afterwards).
        - verbose (bool, optional): verbose mode. Defaults to False.

    Raises:
        NotImplementedError: AOD apriori is not implemented yet.

    Returns:
        :class:`aprofiles.profiles.ProfilesData` object with additional :class:`xarray.DataArray`.
            - `'extinction' (time, altitude)`: 2D array corresponding to the aerosol extinction, in km-1.
            - `'aod' (time)`: 1D array corresponding to the aerosol optical depth associated to the extinction profiles.
            - `'lidar_ratio' (time)`: 1D array corresponding to the lidar ratio associated to the extinction profiles.


        Example:
            Profiles preparation

            >>> import aprofiles as apro
            >>> #read example file
            >>> path = "examples/data/L2_0-20000-001492_A20210909.nc"
            >>> reader = apro.reader.ReadProfiles(path)
            >>> profiles = reader.read()
            >>> #extrapolate lowest layers
            >>> profiles.extrapolate_below(z=150, inplace=True)

            Backward inversion

            >>> #aerosol inversion
            >>> profiles.inversion(zmin=4000, zmax=6000, remove_outliers=False, method='backward')
            >>> #plot extinction profiles
            >>> profiles.plot(var='extinction', zmax=6000, vmin=0, vmax=5e-2)

            .. figure:: ../../docs/_static/images/backward.png
                :scale: 50 %
                :alt: clouds detection

                Extinction profiles retrieved with the backward method.

            Forward inversion

            >>> #aerosol inversion
            >>> profiles.inversion(zmin=4000, zmax=6000, remove_outliers=False, method='forward')
            >>> #plot extinction profiles
            >>> profiles.plot(var='extinction', zmax=6000, vmin=0, vmax=5e-2)

            .. figure:: ../../docs/_static/images/forward.png
                :scale: 50 %
                :alt: clouds detection

                Extinction profiles retrieved with the forward method.
    """

    # we work on profiles averaged in time to reduce the noise
    rcs = profiles.time_avg(
        time_avg, var="attenuated_backscatter_0", inplace=False
    ).data.attenuated_backscatter_0

    """
    #if clouds detected, set to nan profiles where cloud is found below 4000m
    lowest_clouds = profiles._get_lowest_clouds()
    for i in range(len(profiles.data.time.data)):
        if lowest_clouds[i]<=4000:
            rcs.data[i,:] = [np.nan for _ in rcs.data[i,:]]
    """

    # if under_clouds, check if clouds_bases is available
    if under_clouds and "clouds_bases" in list(profiles.data.data_vars):
        lowest_clouds = profiles._get_lowest_clouds()
    elif under_clouds and "clouds_bases" not in list(profiles.data.data_vars):
        warnings.warn(
            "under_clouds parameter sets to True (defaults value) when the clouds detection has not been applied to ProfileData object."
        )
        lowest_clouds = [np.nan for i in np.arange(len(profiles.data.time))]
    else:
        lowest_clouds = [np.nan for i in np.arange(len(profiles.data.time))]

    # aerosol retrieval requires a molecular profile
    altitude = np.asarray(profiles.data.altitude.data)
    wavelength = float(profiles.data.l0_wavelength.data)
    rayleigh = apro.rayleigh.RayleighData(
        altitude, T0=298, P0=1013, wavelength=wavelength
    )

    # aerosol inversion
    ext, lr, aod, z_ref = [], [], [], []
    aod_min, aod_max = 0, 2
    vertical_resolution = profiles._get_resolution("altitude")
    for i in (track(range(len(profiles.data.time.data)), description="klett ",disable=not verbose)):
        # for this inversion, it is important to use the right units
        if "Mm" in profiles.data.attenuated_backscatter_0.units:
            calibrated_data = rcs.data[i, :] * 1e-6 # conversion from Mm-1.sr-1 to m-1.sr-1
        else:
            calibrated_data = rcs.data[i, :]

        # reference altitude
        lowest_cloud_agl = lowest_clouds[i] - profiles.data.station_altitude.data
        imin = profiles._get_index_from_altitude_AGL(zmin)
        imax = profiles._get_index_from_altitude_AGL(np.nanmin([zmax, lowest_cloud_agl]))
        if method == "backward":
            iref = get_iref(rcs.data[i, :], imin, imax, min_snr)
        elif method == "forward":
            iref = imax
        z_ref.append(altitude[iref])

        if iref is not None:
            # aerosol inversion
            if method == "backward":
                _ext = backward_inversion(calibrated_data, iref, apriori, rayleigh)
            elif method == "forward":
                _ext = forward_inversion(calibrated_data, iref, apriori, rayleigh)
        else:
            _ext = [np.nan for _ in range(len(calibrated_data))]

        # add aod and lr
        if "aod" in apriori:
            # search by dichotomy the LR that matches the apriori aod
            raise NotImplementedError("AOD apriori is not implemented yet")
        else:
            # if we assume the LR, no need to minimize for matching aod
            _lr = apriori["lr"]
            _aod = np.nancumsum(np.asarray(_ext) * vertical_resolution)[-1]
            if remove_outliers and _aod < aod_min or remove_outliers and _aod > aod_max:
                lr.append(np.nan)
                aod.append(np.nan)
                ext.append([np.nan for x in _ext])
            else:
                lr.append(_lr)
                aod.append(_aod)
                ext.append(_ext)

    # creates dataarrays
    profiles.data["extinction"] = (("time","altitude"), np.asarray(ext) * 1e3)
    profiles.data["extinction"] = profiles.data.extinction.assign_attrs({
        'long_name': f"Extinction Coefficient @ {int(wavelength)} nm",
        'method': f"{method.capitalize()} Klett",
        'units': "km-1",
        'time_avg': time_avg,
        'zmin': zmin,
        'zmax': zmax,
        'apriori_variable': list(apriori.keys())[0],
        'apriori_value': apriori[list(apriori.keys())[0]],
        })

    profiles.data["aod"] = ("time", aod)
    profiles.data["aod"] = profiles.data.aod.assign_attrs({
        'long_name': f"Aerosol Optical Depth @ {int(wavelength)} nm",
        'unit': ''
    })

    profiles.data["lidar_ratio"] = ('time', lr)
    profiles.data["lidar_ratio"] = profiles.data.lidar_ratio.assign_attrs({
        'long_name': f"Lidar Ratio @ {int(wavelength)} nm",
        'units': 'sr'
    })

    profiles.data["z_ref"] = ('time', z_ref)
    profiles.data["z_ref"] = profiles.data.z_ref.assign_attrs({
        'long_name': f"Reference altitude ASL",
        'units': 'm'
    })

    return profiles
