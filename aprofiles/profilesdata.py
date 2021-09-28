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
        else:
            raise NotImplementedError('Linear extrapolation is not implemented yet')

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


    def quickplot(self,var='attenuated_backscatter_0', vmin=0, vmax=None, log=False, cmap='Spectral_r'):
        """Plot 2D Quicklook

        Args:
            var (str, optional): Variable of ProfilesData.data Dataset to be plotted. Defaults to 'attenuated_backscatter_0'.
            vmin (int, optional): Minimum value. Defaults to 0.
            vmax (int, optional): Maximum value. If None, calculates max from data.
            log (bool, optional), Use logarithmic scale. Defaults to None.
            cmap (str, optional): Matplotlib colormap. Defaults to 'Spectral_r'.
        """
        import matplotlib.pyplot as plt

        #calculcates max value from data
        if vmax==None:
            perc = np.percentile(self.data[var].data,70)
            pow10 = np.ceil(np.log10(perc))
            vmax = 10**(pow10)

        fig, axs = plt.subplots(1, 1, figsize=(6, 3))
        #plot image
        #plt.imshow(self.data[self.var],origin='lower')
        X = self.data.time
        Y = self.data.altitude
        C = np.transpose(self.data[var].values)

        if log:
            import matplotlib.colors as colors
            plt.pcolormesh(X, Y, C, norm=colors.LogNorm(vmin=np.max([1e-3,vmin]), vmax=vmax), cmap=cmap, shading='nearest')
        else:
            plt.pcolormesh(X, Y, C, vmin=vmin, vmax=vmax, cmap=cmap, shading='nearest')
        
        #set title and axis
        yyyy = pd.to_datetime(self.data.time.values[0]).year
        mm = pd.to_datetime(self.data.time.values[0]).month
        dd = pd.to_datetime(self.data.time.values[0]).day
        station_id = self.data.attrs['site_location']
        plt.title('{} - {}/{:02}/{:02}'.format(station_id, yyyy, mm, dd))
        plt.xlabel('Time')
        plt.ylabel('Altitude ASL (m)')
        
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
    profiles.gaussian_filter(sigma=0.5, inplace=True)
    profiles.quickplot(log=True, vmin=10, vmax=1e4, cmap='viridis')


if __name__ == '__main__':
    _main()

