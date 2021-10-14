#!/usr/bin/env python3
import numpy as np
import xarray as xr
from tqdm import tqdm


def detect_pbl(self, time_avg=1, zmin=100., zmax=3000., wav_width=200., under_clouds=True, min_snr=2., verbose=False):
    """Module for *Planetary Boundary Layer Height* detection.
    Detects Planetary Boundary Layer Height between zmin and zmax by looking at the maximum vertical gradient in each individual profiles.

    Args:
        - time_avg (int, optional): in minutes, the time during which we aggregate the profiles before detecting the PBL. Defaults to `1`.
        - zmin (float, optional): maximum altitude AGL, in m, for retrieving the PBL. Defaults to `100`.
        - zmin (float, optional): minimum altitude AGL, in m, for retrieving the PBL. Defaults to `3000`.
        - wav_width (float, optional): Width of the wavelet used in the convolution, in m. Defaults to `200`.
        - under_clouds (bool, optional): If True, and if clouds detection have been called before, force the PBL to be found below the first cloud detected in the profile. Defaults to `True`.
        - min_snr (float, optional). Minimum SNR at the retrieved PBL height required to return a valid value. Defaults to `2.`.
        - verbose (bool, optional): verbose mode. Defaults to `False`.
    
    Returns:
        :class:`ProfilesData` object with additional Data Array.
            - :class:`xarray.DataArray 'pbl' (time, altitude)`: mask array corresponding to the pbl height.
    
        Example:

        >>> import aprofiles as apro
        >>> #read example file
        >>> path = "examples/data/L2_0-20000-001492_A20210909.nc"
        >>> reader = apro.reader.ReadProfiles(path)
        >>> profiles = reader.read()
        >>> #pbl detection
        >>> profiles.pbl(zmin=100., zmax=3000.)
        >>> #attenuated backscatter image with pbl up to 6km of altitude
        >>> profiles.plot(show_pbl=True, zmax=6000., vmin=1e-2, vmax=1e1, log=True)

        .. figure:: _build/html/_images/pbl.png
            :scale: 50 %
            :alt: clouds detection

            PLanetary Boundary Layer Height detection.
    """

    from scipy.ndimage.filters import uniform_filter1d

    def _snr_at_iz(array, iz, step):
        #calculates the snr from array at iz around step points
        gates = np.arange(iz-step,iz+step)
        indexes = [i for i in gates if i>0 and i<len(array)]
        mean = np.nanmean(array[indexes])
        std = np.nanstd(array[indexes], ddof=0)
        if std!=0:
            return mean/std
        else:
            return 0


    def _detect_pbl_from_rcs(data, zmin, zmax, wav_width, min_snr):
        #detect pbl from range corrected signal between zmin and zmax using convolution with a wavelet..
        """
        from scipy import signal
        
        #define wavelet with constant width
        npoints = len(data)
        width = wav_width #in meter
        wav = signal.ricker(npoints, width/self._get_resolution('altitude'))
        
        #simple convolution
        convolution = signal.convolve(data, wav, mode='same')

        #the PBL is the maximum of the convolution
        #sets to nan outside of PBL search range
        convolution[0:self._get_index_from_altitude_AGL(zmin):] = np.nan
        convolution[self._get_index_from_altitude_AGL(zmax):] = np.nan
        i_pbl = np.nanargmax(abs(convolution))
        """

        #0. rolling average
        avg_data = uniform_filter1d(data, size=10)

        #simple gradient
        gradient = np.gradient(avg_data)

        #the PBL is the maximum of the convolution
        #sets to nan outside of PBL search range
        gradient[0:self._get_index_from_altitude_AGL(zmin):] = np.nan
        gradient[self._get_index_from_altitude_AGL(zmax):] = np.nan
        i_pbl = np.nanargmin(gradient)
        
        
        #calculates SNR
        snr =  _snr_at_iz(data, i_pbl, step=10)
        if snr>min_snr:
            return self.data.altitude.data[i_pbl]
        else:
            return np.nan
    
    #we work on profiles averaged in time to reduce the noise
    rcs = self.time_avg(time_avg, var='attenuated_backscatter_0', inplace=False).data.attenuated_backscatter_0


    #if under_clouds, check if clouds_bases is available
    if under_clouds and 'clouds_bases' in list(self.data.data_vars):
        lowest_clouds = self._get_lowest_clouds()
    elif under_clouds and not 'clouds_bases' in list(self.data.data_vars):
        import warnings
        warnings.warn("under_clouds parameter sets to True (defaults value) when the clouds detection has not been applied to ProfileData object.")
        lowest_clouds = [np.nan for _ in np.arange(len(self.data.time))]
    else:
        lowest_clouds = [np.nan for _ in np.arange(len(self.data.time))]
    

    pbl = []
    for i in (tqdm(range(len(self.data.time.data)),desc='pbl   ') if verbose else range(len(self.data.time.data))):
        lowest_cloud_agl = lowest_clouds[i] - self.data.station_altitude.data
        pbl.append(_detect_pbl_from_rcs(rcs.data[i,:], zmin, np.nanmin([zmax, lowest_cloud_agl]), wav_width, min_snr))

    #creates dataarrays
    self.data["pbl"] = xr.DataArray(
        data=pbl,
        dims=["time"],
        coords=dict(
            time=self.data.time.data
        ),
        attrs=dict(
            long_name="Planetary Boundary Layer Height, ASL",
            units="m",
            time_avg=time_avg,
            zmin=zmin,
            zmax=zmax
        )
    )
    return self

def _main():
    import aprofiles as apro
    path = "data/e-profile/2021/09/09/L2_0-20000-001492_A20210909.nc"
    profiles = apro.reader.ReadProfiles(path).read()

    #basic corrections
    profiles.extrapolate_below(z=150, inplace=True)
    #detection
    profiles.pbl(zmin=300, zmax=3000,wav_width=200, under_clouds=False, min_snr=2, verbose=True)
    profiles.plot(show_pbl=True, log=True, vmin=1e-2, vmax=1e1)
    #plot single profile
    datetime = np.datetime64('2021-09-09T21:20:00')
    profiles.plot(datetime=datetime, vmin=-1, vmax=10, zmax=12000, show_pbl=True)


if __name__ == '__main__':
    _main()
