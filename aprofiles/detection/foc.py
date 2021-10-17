#!/usr/bin/env python3
import numpy as np
import xarray as xr
from tqdm import tqdm

def detect_foc(self, method='cloud_base', var='attenuated_backscatter_0', z_snr=2000., min_snr=2., zmin_cloud=200.):
        """Detects fog or condensation.

        Args:
            - method ({'cloud_base', 'snr'}, optional): Defaults to `'cloud_base'`.
            - var (str, optional). Used for 'snr' method. Variable from ProfilesData to calculate SNR from. Defaults to `'attenuated_backscatter_0'`.
            - z_snr (float, optional): Used for 'snr' method. Altitude AGL (in m) at which we calculate the SNR. Defaults to `2000.`.
            - min_snr (float, optional): Used for 'snr' method. Minimum SNR under which the profile is considered as containing fog or condensation. Defaults to `2.`.
            - zmin_cloud (float, optional): Used for 'cloud_base' method. Altitude AGL (in m) below which a cloud base height is considered a fog or condensation situation. Defaults to `200.`.
        
        Returns:
            :class:`ProfilesData` object with additional Data Array.
                - :class:`xarray.DataArray 'foc' (time)`: mask array corresponding to the presence of foc.
    
        Example:

        >>> import aprofiles as apro
        >>> #read example file
        >>> path = "examples/data/L2_0-20000-001492_A20210909.nc"
        >>> reader = apro.reader.ReadProfiles(path)
        >>> profiles = reader.read()
        >>> #foc detection
        >>> profiles.foc()
        >>> #attenuated backscatter image with pbl up to 6km of altitude
        >>> profiles.plot(show_pbl=True, zmax=6000., vmin=1e-2, vmax=1e1, log=True)

        .. figure:: _static/_images/foc.png
            :scale: 50 %
            :alt: foc detection

            Fog or condensation (foc) detection.
        """

        def _detect_fog_from_cloud_base_height(self, zmin_cloud):
            #returns a bool list with True where fog/condensation cases
            #if the base of the first cloud (given by the constructor) is below 
            first_cloud_base_height = self.data.cloud_base_height.data[:,0]
            #condition
            foc = [True if x<=zmin_cloud else False for x in first_cloud_base_height]
            return foc
        
        def _detect_fog_from_snr(self, z_snr, var, min_snr):
            #returns a bool list with True where fog/condensation cases

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

            #calculates snr at z_snr
            iz_snr = self._get_index_from_altitude_AGL(z_snr)
            #calculates snr at each timestamp
            snr = [_snr_at_iz(self.data[var].data[i,:], iz_snr, step=4) for i in range(len(self.data.time.data))]
            #condition
            foc = [True if x<=min_snr else False for x in snr]
            return foc


        if method=='cloud_base':
            foc = _detect_fog_from_cloud_base_height(self, zmin_cloud)
        elif method.upper() == 'SNR':
            foc = _detect_fog_from_snr(self, z_snr, var, min_snr)

        #creates dataarray
        self.data["foc"] = xr.DataArray(
            data=foc,
            dims=["time"],
            coords=dict(
                time=self.data.time.data,
            ),
            attrs=dict(
                long_name="Fog or condensation mask.",
            )
        )

        return self