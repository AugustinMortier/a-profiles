#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles Profiles

import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import pandas as pd

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


    def quickplot(self,var='attenuated_backscatter_0', vmin=0, vmax=1, cmap='Spectral_r'):
        fig, axs = plt.subplots(1, 1, figsize=(6, 3))
        #plot image
        #plt.imshow(self.data[self.var],origin='lower')
        X = self.data.time
        Y = self.data.altitude
        C = np.transpose(self.data[var].values)
        plt.pcolormesh(X, Y, C, vmin=vmin, vmax=vmax, cmap=cmap, shading='nearest')
        
        #set title and axis
        yyyy = pd.to_datetime(self.data.time.values[0]).year
        mm = pd.to_datetime(self.data.time.values[0]).month
        dd = pd.to_datetime(self.data.time.values[0]).day
        station_id = self.data.instrument_id
        plt.title('{} - {}/{:02}/{:02}'.format(station_id, yyyy, mm, dd))
        plt.xlabel('Time')
        plt.ylabel('Altitude (m)')
        
        #colorbar
        cbar = plt.colorbar()
        cbar.set_label('Attenuated backscatter Signal')

        plt.tight_layout()
        plt.show()


def main():
    import reader
    path = "data/e-profile/2021/09/08/L2_0-20000-006735_A20210908.nc"
    profiles = reader.ReadProfiles(path).read()
    profiles.quickplot('attenuated_backscatter_0', vmin=0, vmax=1, cmap='viridis')


if __name__ == '__main__':
    main()

