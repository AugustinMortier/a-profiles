#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles - Aerosol Inversion

import aprofiles as apro
import numpy as np
import xarray as xr
from scipy.ndimage.filters import uniform_filter1d
from tqdm import tqdm
import warnings

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

    if 'aod' in apriori:
        #search by dichotomy the LR that matches the apriori aod
        raise NotImplementedError('AOD apriori is not implemented yet')
        lr_aer = 50
    else:
        #if we assume the LR, no need to minimize for matching aod 
        lr_aer = apriori['lr']
    lr_mol = 8.*np.pi/3.

    #vertical resolution
    dz = min(np.diff(rayleigh.altitude))

    int1_a = np.cumsum((lr_aer-lr_mol)*rayleigh.backscatter[:iref]*dz)
    int1_b = [2*int1_a[-1] - 2*int1_a[i] for i in range(iref)]
    phi = [np.log(abs(data[i]/data[iref])) + int1_b[i] for i in range(iref)]

    int2_a = 2*np.nancumsum(lr_aer*np.exp(phi)*dz)
    int2_b = [int2_a[-1] - int2_a[i] for i in range(iref)]

    #initialize total backscatter
    back_aer_iref = 0 #m-1
    beta_tot_iref = rayleigh.backscatter[iref] + back_aer_iref

    #total backscatter
    beta_tot = [np.exp(phi[i])/((1/beta_tot_iref)+int2_b[i]) for i in range(iref)]
    #aerosol backsatter (m-1.sr-1)
    beta_aer = beta_tot - rayleigh.backscatter[:iref]
    #aerosol extinction (m-1)
    sigma_aer=lr_aer*beta_aer
    #returns extinction in m-1 when valid, and np.nan elsewhere
    ext = [sigma_aer[i] if i<len(sigma_aer) else np.nan for i in range(len(data))]
    return ext

def forward_inversion(data, iref, apriori, rayleigh):
    """Forward iterative inversion method [#]_.

    .. [#] Li, D., Wu, Y., Gross, B., & Moshary, F. (2021). Capabilities of an Automatic Lidar Ceilometer to Retrieve Aerosol Characteristics within the Planetary Boundary Layer. Remote Sensing, 13(18), 3626.
    
    Method principle: 
    
    At z0, the aerosol transmission is first assumed a being close to 1. We evaluate the aerosol extinction based on this assumption. 
    This evaluation gives a refined aerosol extinction that is used to calculate a second time the aerosol transmission.
    The aerosol extinction retrieval will converge after a certain number iterations.
    After the convergence, the aerosol extinction is retrieved in the next upper layer.

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

    if 'aod' in apriori:
        #search by dichotomy the LR that matches the apriori aod
        raise NotImplementedError('AOD apriori is not implemented yet')
        lr_aer = 50
    else:
        #if we assume the LR, no need to minimize for matching aod 
        lr_aer = apriori['lr']
    lr_mol = 8.*np.pi/3.
    
    def _get_aer_at_i(data, i, Tm, Bm, Ta, Ba, Ea, nloop_max=30, diff_ext=0.01):
        for _ in range(nloop_max):
            if np.isnan(Ea[0]):
                Ta[i] = 1
            else:
                Ta[i] = np.exp(-2*np.nancumsum(Em*dz))[i]
            Ba[i] = data[i]/(Tm[i]**2*Ta[i]**2) - Bm[i]
            #test extinction
            if 1 - (lr_aer * Ba[i] / Ea[i]) < diff_ext:
                Ea[i] = lr_aer * Ba[i]
                break
            Ea[i] = lr_aer * Ba[i]

        return Ba[i], Ea[i], Ta[i]
    
    #vertical resolution
    dz = min(np.diff(rayleigh.altitude))
    
    Bm = rayleigh.backscatter
    Em = rayleigh.extinction
    Tm = np.exp(-2*np.cumsum(Em*dz))

    #Initialize aer profiles
    Ta = np.asarray([np.nan for _ in range(len(data))])
    Ba = np.asarray([np.nan for _ in range(len(data))])
    Ea = np.asarray([np.nan for _ in range(len(data))])

    for i in range(iref):
        Ba[i], Ea[i], Ta[i] = _get_aer_at_i(data, i, Tm, Bm, Ta, Ba, Ea)
    #returns extinction in m-1
    ext = Ea
    return ext


def inversion(self, time_avg=1, zmin=4000., zmax=6000., min_snr=0., under_clouds=False, method='forward', apriori={'lr': 50.}, remove_outliers=False, verbose=False):
    """Aerosol inversion of the attenuated backscatter profiles using an apriori.

    Args:
        - time_avg (int, optional): in minutes, the time during which we aggregate the profiles before inverting the profiles. Defaults to 1.
        - zmin (float, optional): minimum altitude AGL, in m, for looking for the initialization altitude. Defaults to 4000..
        - zmax (float, optional): maximum altitude AGL, in m, for looking for the initialization altitude. Defaults to 6000..
        - min_snr (float, optional). Minimum SNR required at the reference altitude to be valid. Defaults to 0.
        - under_clouds (bool, optional): If True, and if the `ProfilesData` has a `cloud_base` variable (returned by the `clouds` method), forces the initialization altitude to be found below the first cloud detected in the profile. Defaults to True.
        - method ({‘backward’, ‘forward’}, optional). Defaults to ‘forward’.
        - apriori (dict, optional). A priori value to be used to constrain the inversion. Valid keys: ‘lr’ (Lidar Ratio, in sr) and ‘aod’ (unitless). Defaults to {‘lr’: 50}.
        - remove_outliers (bool, optional). Remove profiles considered as outliers based on aod calculation ([>0, <1]). Defaults to False (while development. to be changed afterwards).
        - verbose (bool, optional): verbose mode. Defaults to False.

    Raises:
        NotImplementedError: AOD apriori is not implemented yet.

    Returns:
        :class:`aprofiles.profiles.ProfilesData` object with additional :class:`xarray.DataArray`.
            - `'extinction' (time, altitude)`: 2D array corresponding to the aerosol extinction.
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

            .. figure:: ../examples/images/backward.png
                :scale: 50 %
                :alt: clouds detection

                Extinction profiles retrieved with the backward method.
            
            Forward inversion

            >>> #aerosol inversion
            >>> profiles.inversion(zmin=4000, zmax=6000, remove_outliers=False, method='backward')
            >>> #plot extinction profiles
            >>> profiles.plot(var='extinction', zmax=6000, vmin=0, vmax=5e-2)

            .. figure:: ../examples/images/forward.png
                :scale: 50 %
                :alt: clouds detection

                Extinction profiles retrieved with the forward method.
    """

    #we work on profiles averaged in time to reduce the noise
    rcs = self.time_avg(time_avg, var='attenuated_backscatter_0', inplace=False).data.attenuated_backscatter_0

    """
    #if clouds detected, set to nan profiles where cloud is found below 4000m
    lowest_clouds = self._get_lowest_clouds()
    for i in range(len(self.data.time.data)):
        if lowest_clouds[i]<=4000:
            rcs.data[i,:] = [np.nan for _ in rcs.data[i,:]]
    """

    #if under_clouds, check if clouds_bases is available
    if under_clouds and 'clouds_bases' in list(self.data.data_vars):
        lowest_clouds = self._get_lowest_clouds()
    elif under_clouds and not 'clouds_bases' in list(self.data.data_vars):
        warnings.warn("under_clouds parameter sets to True (defaults value) when the clouds detection has not been applied to ProfileData object.")
        lowest_clouds = [np.nan for i in np.arange(len(self.data.time))]
    else:
        lowest_clouds = [np.nan for i in np.arange(len(self.data.time))]
    
    #aerosol retrieval requires a molecular profile
    altitude = np.asarray(self.data.altitude.data)
    wavelength = float(self.data.l0_wavelength.data)
    rayleigh = apro.rayleigh.RayleighData(altitude, T0=298, P0=1013, wavelength=wavelength);


    #aerosol inversion
    ext, lr, aod = [], [], []
    aod_min, aod_max = 0, 0.5
    vertical_resolution = self._get_resolution('altitude')
    for i in (tqdm(range(len(self.data.time.data)),desc='klett ') if verbose else range(len(self.data.time.data))):
        #for the inversion, it is important to use the right units
        if 'E-6' in self.data.attenuated_backscatter_0.units:
            calibrated_data = rcs.data[i,:]*1e-6
        else:
            calibrated_data = rcs.data[i,:]

        #reference altitude
        lowest_cloud_agl = lowest_clouds[i] - self.data.station_altitude.data
        imin = self._get_index_from_altitude_AGL(zmin)
        imax = self._get_index_from_altitude_AGL(np.nanmin([zmax, lowest_cloud_agl]))
        iref = get_iref(rcs.data[i,:], imin, imax, min_snr)

        if iref!=None:
            #aerosol inversion
            if method=='backward':
                _ext = backward_inversion(calibrated_data, iref, apriori, rayleigh)
            elif method=='forward':
                _ext = forward_inversion(calibrated_data, iref, apriori, rayleigh)
        else:
            _ext = [np.nan for _ in range(len(calibrated_data))]

        #add aod and lr
        if 'aod' in apriori:
                #search by dichotomy the LR that matches the apriori aod
                raise NotImplementedError('AOD apriori is not implemented yet')
        else:
            #if we assume the LR, no need to minimize for matching aod
            _lr = apriori['lr']
            _aod = np.nancumsum(np.asarray(_ext)*vertical_resolution)[-1]
            if remove_outliers and _aod<aod_min or remove_outliers and _aod>aod_max:
                lr.append(np.nan)
                aod.append(np.nan)
                ext.append([np.nan for x in _ext])
            else:
                lr.append(_lr)
                aod.append(_aod)
                ext.append(_ext)


    #creates dataarrays
    self.data["extinction"] = xr.DataArray(
        data=np.asarray(ext)*1e3,
        dims=["time", "altitude"],
        coords=dict(
            time=self.data.time.data,
            altitude=self.data.altitude.data
        ),
        attrs=dict(
            long_name="Extinction Coefficient at {} nm".format(int(wavelength)),
            method="{} Klett".format(method.capitalize()),
            units="km-1",
            time_avg=time_avg,
            zmin=zmin,
            zmax=zmax,
            apriori=apriori
        )
    )

    self.data["aod"] = xr.DataArray(
        data=aod,
        dims=["time"],
        coords=dict(
            time=self.data.time.data
        ),
        attrs=dict(
            long_name="Aerosol Optical Depth",
            units=None
        )
    )

    self.data["lidar_ratio"] = xr.DataArray(
        data=lr,
        dims=["time"],
        coords=dict(
            time=self.data.time.data
        ),
        attrs=dict(
            long_name="Lidar Ratio",
            units="sr"
        )
    )
    return self
