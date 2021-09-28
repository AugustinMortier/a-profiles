#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles ProfilesData

import copy
import numpy as np
import pandas as pd
import xarray as xr


class ProfilesData:
    """Base class representing profiles data.
    """

    def __init__(self, data):
        self.data = data

    @property 
    def data(self): 
        """Data attribute (instance of :class:`xarray.Dataset`)
        """
        return self._data 
    
    @data.setter 
    def data(self, data):
        if not isinstance(data, xr.Dataset):
            raise ValueError("Wrong data type: an xarray Dataset is expected.")
        self._data = data



    def gaussian_filter(self, var='attenuated_backscatter_0', sigma=0.5, inplace=False):
        """Function that applies a 2D gaussian filter in order to reduce high frequency noise.

        Args:
            var (str, optional): variable of the Dataset to be processed. Defaults to 'attenuated_backscatter_0'.
            sigma (scalar or sequence of scalars, optional): Standard deviation for Gaussian kernel. The standard deviations of the Gaussian filter are given for each axis as a sequence, or as a single number, in which case it is equal for all axes. Defaults to 0.
            inplace (bool, optional): if True, replace the variable, else use a copy. Defaults to False.
        
        Returns:
            ProfilesData object
        """
        import copy

        from scipy.ndimage import gaussian_filter

        #apply gaussian filter
        filtered_data = gaussian_filter(self.data[var].data, sigma=sigma)

        if inplace:
            self.data[var].data = filtered_data
            new_dataset = self
        else:
            copied_dataset = copy.deepcopy(self)
            copied_dataset.data[var].data = filtered_data
            new_dataset = copied_dataset
        #add attribute
        new_dataset.data[var].attrs['gaussian filter']=sigma
        return new_dataset



    def extrapolation_lowest_layers(self, var='attenuated_backscatter_0', zmin=0, method='cst', inplace=False):
        """Method for extrapolating lowest layers below a certain altitude. This is of particular intrest for instruments subject to After Pulse effect, with saturated signal in the lowest layers.

        Args:
            var (str, optional): variable of the Dataset to be processed. Defaults to 'attenuated_backscatter_0'.
            zmin (float, optional): Altitude (in m, AGL) below which the signal is extrapolated. Defaults to 0.
            method (str, optional): 'cst' or 'lin' Method to be used for extrapolation of lowest layers. Defaults to 'cst'.
            inplace (bool, optional): if True, replace the variable. Defaults to False.
        
        Returns:
            ProfilesData object
        """

        #get index of zmin
        zmin_asl = zmin + self.data.station_altitude.data
        imin = np.argmin(abs(self.data.altitude.data-zmin_asl))
        
        nt = np.shape(self.data[var].data)[0]

        if method == 'cst':
            #get values at imin
            data_zmin = self.data[var].data[:,imin]
            #generates ones matrice with time/altitude dimension to fill up bottom
            ones = np.ones((nt,imin))
            #replace values
            filling_matrice = np.transpose(np.multiply(np.transpose(ones),data_zmin))
        elif method == 'lin':
            raise NotImplementedError('Linear extrapolation is not implemented yet')
        else:
            raise ValueError('Expected string: lin or cst')

        if inplace:
            self.data[var].data[:,0:imin] = filling_matrice
            new_dataset = self
        else:
            copied_dataset = copy.deepcopy(self)
            copied_dataset.data[var].data[:,0:imin] = filling_matrice
            new_dataset = copied_dataset
        
        #add attributes
        new_dataset.data[var].attrs['extrapolation_low_layers_altitude_agl']=zmin
        new_dataset.data[var].attrs['extrapolation_low_layers_method']=method
        return new_dataset


    
    def range_correction(self, var='attenuated_backscatter_0', inplace=False):
        """Method that corrects the solid angle effect (1/z2) which makes that the backscatter beam more unlikely to be detected with the square of the altitude.

        Args:
            var (str, optional): variable of the Dataset to be processed. Defaults to 'attenuated_backscatter_0'.
            inplace (bool, optional): if True, replace the variable. Defaults to False.
        
        Returns:
            ProfilesData object
        """

        #for the altitude correction, must one use the altitude above the ground level
        z_agl = self.data.altitude.data - self.data.station_altitude.data
        
        data = self.data[var].data
        range_corrected_data = np.multiply(data,z_agl)

        if inplace:
            self.data[var].data = range_corrected_data
            new_profiles_data = self
        else:
            copied_dataset = copy.deepcopy(self)
            copied_dataset.data[var].data = range_corrected_data
            new_profiles_data = copied_dataset

        #add attribute
        new_profiles_data.data[var].attrs['range correction']=True
        return new_profiles_data



    def detect_fog_or_condensation(self, zmin):
        """Detects fog or condensation relying on the cloud base height 'cloud_base_height' given by the constructor.
        Adds DataArray to DataSet

        Args:
            zmin (float): Altitude AGL (in m) below which a cloud base height is considered a fog or condensation situation. Note: 200 m seems to give good results.
            add_dataarray (bool, optional): Add dataset to datarray if True. Defaults to True.
        
        Returns:
            :class: `ProfilesData object` with additional data array 'fog_or_condensation'.
        """

        first_cloud_base_height = self.data.cloud_base_height.data[:,0]
        fog_or_condensation = [True if x<=zmin else False for x in first_cloud_base_height]

        #creates dataarray
        self.data["fog_or_condensation"] = xr.DataArray(
            data=fog_or_condensation,
            dims=["time"],
            coords=dict(
                time=self.data.time.data,
            ),
            attrs=dict(
                description="Fog or condensation mask.",
            )
        )

        return self


    def quickplot(self,var='attenuated_backscatter_0', zmin=None, zmax= None, vmin=0, vmax=None, log=False, add_fog=False, add_pbl=False, add_clouds=False, cmap='RdYlBu_r'):
        """Plot 2D Quicklook

        Args:
            var (str, optional): Variable of ProfilesData.data Dataset to be plotted. Defaults to 'attenuated_backscatter_0'.
            zmin (float, optional): Minimum altitude AGL (m). Defaults to minimum available altitude.
            zmax (float, optional): Maximum altitude AGL (m). Defaults to maximum available altitude.
            vmin (float, optional): Minimum value. Defaults to 0.
            vmax (float, optional): Maximum value. If None, calculates max from data.
            log (bool, optional), Use logarithmic scale. Defaults to None.
            add_fog (bool, optional): Add fog detection. Defaults to False.
            add_pbl (bool, optional): Add PBL height. Defaults to False.
            add_clouds (bool, optional): Add clouds detection. Defaults to False.
            cmap (str, optional): Matplotlib colormap. Defaults to 'Spectral_r'.
        """
        import matplotlib.pyplot as plt

        #calculcates max value from data
        if vmax==None:
            perc = np.percentile(self.data[var].data,70)
            pow10 = np.ceil(np.log10(perc))
            vmax = 10**(pow10)

        #altitude range
        if zmin==None:
            imin = 0
        else:
            zmin_asl = zmin + self.data.station_altitude.data
            imin = np.argmin(abs(self.data.altitude.data-zmin_asl))
        if zmax==None:
            imax=len(self.data.altitude)
        else:
            zmax_asl = zmax + self.data.station_altitude.data
            imax = np.argmin(abs(self.data.altitude.data-zmax_asl))


        #plot image
        X = self.data.time
        Y = self.data.altitude - self.data.station_altitude.data
        C = np.transpose(self.data[var].values)

        #limit to altitude range
        Y = Y[imin:imax]
        C = C[imin:imax,:]

        fig, axs = plt.subplots(1, 1, figsize=(6, 2))
        if log:
            import matplotlib.colors as colors
            plt.pcolormesh(X, Y, C, norm=colors.LogNorm(vmin=np.max([1e-3,vmin]), vmax=vmax), cmap=cmap, shading='nearest')
        else:
            plt.pcolormesh(X, Y, C, vmin=vmin, vmax=vmax, cmap=cmap, shading='nearest')
        
        #add addition information
        if add_fog:
            fog_markers = [1 if x==True else np.nan for x in self.data.fog_or_condensation.data]
            plt.plot(X, fog_markers,"^:m",lw=0, label='fog or condensation')
        
        #set title and axis
        yyyy = pd.to_datetime(self.data.time.values[0]).year
        mm = pd.to_datetime(self.data.time.values[0]).month
        dd = pd.to_datetime(self.data.time.values[0]).day
        latitude = self.data.station_latitude.data
        longitude = self.data.station_longitude.data
        altitude = self.data.station_altitude.data
        station_id = self.data.attrs['site_location']
        plt.title('{} ({:.2f};{:.2f}) - Alt: {} m - {}/{:02}/{:02}'.format(station_id, latitude, longitude, altitude, yyyy, mm, dd), weight='bold')
        plt.xlabel('Time')
        plt.ylabel('Altitude AGL (m)')
        
        #add legend
        plt.legend()

        #colorbar
        cbar = plt.colorbar()
        cbar.set_label(self.data[var].long_name)

        plt.tight_layout()
        plt.show()
    


def _main():
    import aprofiles as apro
    path = "data/e-profile/2021/09/08/L2_0-20000-006735_A20210908.nc"
    path = "data/e-profile/2021/09/09/L2_0-20000-001492_A20210909.nc"
    profiles = apro.reader.ReadProfiles(path).read()
    #profiles.quickplot('attenuated_backscatter_0', vmin=0, vmax=1, cmap='viridis')
    profiles.range_correction(inplace=True)
    profiles.gaussian_filter(sigma=0.0, inplace=True)
    profiles.extrapolation_lowest_layers(zmin=500, inplace=True)
    #profiles.quickplot(zmax=10000, vmin=1e1, vmax=1e5, log=True,cmap='viridis')

    profiles.detect_fog_or_condensation(zmin=200)
    profiles.quickplot(zmin=0, zmax=10000, vmin=1e2, vmax=1e5, log=True, add_fog=True)

if __name__ == '__main__':
    _main()

