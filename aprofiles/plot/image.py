#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles - Image plot

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _plot_fog(da, time):
    """Plot fog at the bottom of the image
    Args:
        da ([type]): [description]
        time ([type]): [description]
    """    
    fog_markers = [1 if x==True else np.nan for x in da.fog_or_condensation.data]
    plt.plot(time, fog_markers,"^:m",ms=10,lw=0, label='fog or condensation')

def _plot_clouds(da, time, altitude):
    """Plot clouds as markers.
    Args:
        da ([type]): [description]
        time ([type]): [description]
        altitude ([type]): [description]
    """    
    for i in range(len(time)):
        #plot bases
        b_indexes = [i for i, x in enumerate(da.clouds_bases[i,:].data) if x]
        t = [time[i] for _ in b_indexes]
        if i==0:
            plt.plot(t, altitude[b_indexes], 'k.', label='clouds')
        else:
            plt.plot(t, altitude[b_indexes], 'k.')

        #plot peaks
        p_indexes = [i for i, x in enumerate(da.clouds_peaks[i,:].data) if x]
        t = [time[i] for _ in p_indexes]
        plt.plot(t, altitude[p_indexes], 'k.')
        
        #plot tops
        t_indexes = [i for i, x in enumerate(da.clouds_tops[i,:].data) if x]
        t = [time[i] for _ in t_indexes]
        plt.plot(t, altitude[t_indexes], 'k.')
        

def plot(da, var='attenuated_backscatter_0', zmin=None, zmax=None, vmin=0, vmax=None, log=False, show_fog=False, show_pbl=False, show_clouds=False, cmap='RdYlBu_r'):
    """Plot image of profiles.

    Args:
        da (xr.DataArray): DataArray.
        var (str, optional): Variable of the DataArray to be plotted. Defaults to 'attenuated_backscatter_0'.
        zmin (float, optional): Minimum altitude AGL (m). Defaults to minimum available altitude.
        zmax (float, optional): Maximum altitude AGL (m). Defaults to maximum available altitude.
        vmin (float, optional): Minimum value. Defaults to 0.
        vmax (float, optional): Maximum value. If None, calculates max from data.
        log (bool, optional), Use logarithmic scale. Defaults to None.
        show_fog (bool, optional): Add fog detection. Defaults to False.
        show_pbl (bool, optional): Add PBL height. Defaults to False.
        show_clouds (bool, optional): Add clouds detection. Defaults to False.
        cmap (str, optional): Matplotlib colormap. Defaults to 'Spectral_r'.
    """

    #calculates max value from data
    if vmax==None:
        perc = np.percentile(da[var].data,70)
        pow10 = np.ceil(np.log10(perc))
        vmax = 10**(pow10)


    #time
    time = da.time.data #time
    #altitude AGL
    altitude = da.altitude.data - da.station_altitude.data
    #2D array
    C = np.transpose(da[var].data)


    fig, axs = plt.subplots(1, 1, figsize=(5, 1.5))
    if log:
        import matplotlib.colors as colors
        plt.pcolormesh(time, altitude, C, norm=colors.LogNorm(vmin=np.max([1e-3,vmin]), vmax=vmax), cmap=cmap, shading='nearest')
    else:
        plt.pcolormesh(time, altitude, C, vmin=vmin, vmax=vmax, cmap=cmap, shading='nearest')

    #add addition information
    if show_fog:
        _plot_fog(da, time)
    if show_clouds:
        _plot_clouds(da, time, altitude)

    #limit to altitude range
    plt.ylim([zmin,zmax])

    #set title and axis
    yyyy = pd.to_datetime(da.time.values[0]).year
    mm = pd.to_datetime(da.time.values[0]).month
    dd = pd.to_datetime(da.time.values[0]).day
    latitude = da.station_latitude.data
    longitude = da.station_longitude.data
    altitude = da.station_altitude.data
    station_id = da.attrs['site_location']
    plt.title('{} ({:.2f};{:.2f}) - Alt: {} m - {}/{:02}/{:02}'.format(station_id, latitude, longitude, altitude, yyyy, mm, dd), weight='bold')
    plt.xlabel('Time')
    plt.ylabel('Altitude AGL (m)')

    #add legend
    if show_fog or show_clouds or show_pbl:
        plt.legend(loc='upper right')

    #colorbar
    cbar = plt.colorbar()
    cbar.set_label(da[var].long_name)

    plt.tight_layout()
    plt.show()
