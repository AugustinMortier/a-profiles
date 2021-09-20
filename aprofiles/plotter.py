#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles Plotter

import pandas as pd
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

class Plotter:
    def __init__(self, data):    
        self.data = data

    def plot(self, var, **args):
        #if dataset
        if type(self.data) == xr.core.dataset.Dataset:
            _PlotQLFromDataset(self.data, var, **args).plot()

class _PlotQLFromDataset:
    """[summary]

    Args:
        data (dixarray.core.dataset.Datasetct): dataset to be plotted
    """
    def __init__(self, data, var, vmin=0, vmax=1, cmap='Spectral_r'):
        self.data = data
        self.var = var
        self.vmin = vmin
        self.vmax = vmax
        self.cmap = cmap
    
    def plot(self):
        fig, axs = plt.subplots(1, 1, figsize=(6, 3))
        #plot image
        #plt.imshow(self.data[self.var],origin='lower')
        X = self.data.time
        Y = self.data.altitude
        C = np.transpose(self.data[self.var].values)
        vmin =self.vmin
        vmax = self.vmax
        cmap = self.cmap
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

        plt.show()

def main():
    import reader
    path = "data/e-profile/2021/09/08/L2_0-20000-006735_A20210908.nc"
    path = "tests/data/L2_0-20000-006735_A20210908.nc"
    apro_reader = reader.ReadProfiles(path)
    l2_data = apro_reader.read()

    #plot the dataset
    plotter = Plotter(l2_data)
    plotter.plot('attenuated_backscatter_0',vmin=0, vmax=2, cmap='viridis')

if __name__ == '__main__':
    main()
    