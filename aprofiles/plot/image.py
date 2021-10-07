#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles - Image plot

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import seaborn as sns
sns.set_theme()


def _plot_fog(da, zref):
    """Plot fog at the bottom of the image
    Args:
        da ([type]): [description]
    """
    #time
    time = da.time.data
    #altitude
    if zref.upper()=='AGL':
        altitude = da.altitude.data - da.station_altitude.data
    elif zref.upper()=='ASL':
        altitude = da.altitude.data

    fog_markers = [altitude[0] if x==True else np.nan for x in da.foc.data]
    plt.plot([],[],"^m", ms=10, lw=0, label='fog or condensation')
    plt.plot(time, fog_markers,"m", marker=10, ms=10, lw=0)

def _plot_clouds(da, zref):
    """Plot clouds as markers.
    Args:
        da ([type]): [description]
    """
    #time
    time = da.time.data
    #altitude
    if zref.upper()=='AGL':
        altitude = da.altitude.data - da.station_altitude.data
    elif zref.upper()=='ASL':
        altitude = da.altitude.data

    for i in range(len(time)):
        #plot bases
        b_indexes = [i for i, x in enumerate(da.clouds_bases[i,:].data) if x]
        p_indexes = [i for i, x in enumerate(da.clouds_peaks[i,:].data) if x]
        t_indexes = [i for i, x in enumerate(da.clouds_tops[i,:].data) if x]
        """
        #plot line from base to peak
        for j, _ in enumerate(b_indexes):
            y = altitude[b_indexes[j]:p_indexes[j]]
            x = [time[i] for _ in y]
            plt.plot(x, y, 'w-', lw=1.75, alpha=0.9)

        #plot line from peak to base
        for j, _ in enumerate(b_indexes):
            y = altitude[p_indexes[j]:t_indexes[j]]
            x = [time[i] for _ in y]
            plt.plot(x, y, 'w-', lw=1.75, alpha=0.9)
        """
        #plot markers
        t = [time[i] for _ in b_indexes]
        if i==0:
            plt.plot(t, altitude[b_indexes], 'k.', ms=3, label='clouds')
        else:
            plt.plot(t, altitude[b_indexes], 'k.', ms=3)
        t = [time[i] for _ in p_indexes]
        plt.plot(t, altitude[p_indexes], 'k.', ms=3)
        t = [time[i] for _ in t_indexes]
        plt.plot(t, altitude[t_indexes], 'k.', ms=3)

def _plot_pbl(da, zref):
    """Plot PBL as markers
    Args:
        da ([type]): [description]
    """
    #time
    time = da.time.data
    #altitude
    if zref.upper()=='AGL':
        pbl = da.pbl.data - da.station_altitude.data
    elif zref.upper()=='ASL':
        pbl = da.pbl.data
    plt.plot(time, pbl, ".g", ms=5, lw=0, label='PBL')

def plot(da, var='attenuated_backscatter_0', zref='agl', zmin=None, zmax=None, vmin=0, vmax=None, log=False, show_fog=False, show_pbl=False, show_clouds=False, cmap='coolwarm'):
    """Plot image of profiles.

    Args:
        da (xr.DataArray): DataArray.
        var (str, optional): Variable of the DataArray to be plotted. Defaults to 'attenuated_backscatter_0'.
        zref (str,optional): Base for altitude. Expected values: 'agl' (above ground level) or 'asl' (above sea level). Defaults to 'agl'.
        zmin (float, optional): Minimum altitude AGL (m). Defaults to minimum available altitude.
        zmax (float, optional): Maximum altitude AGL (m). Defaults to maximum available altitude.
        vmin (float, optional): Minimum value. Defaults to 0.
        vmax (float, optional): Maximum value. If None, calculates max from data.
        log (bool, optional), Use logarithmic scale. Defaults to None.
        show_fog (bool, optional): Add fog detection. Defaults to False.
        show_pbl (bool, optional): Add PBL height. Defaults to False.
        show_clouds (bool, optional): Add clouds detection. Defaults to False.
        cmap (str, optional): Matplotlib colormap. Defaults to 'coolwarm' cmap from seaborn.
    """

    #calculates max value from data
    if vmax==None:
        perc = np.percentile(da[var].data,70)
        pow10 = np.ceil(np.log10(perc))
        vmax = 10**(pow10)

    #use seaborn coolwarm colormap
    #if cmap=='coolwarm':
    #    cmap = sns.color_palette("coolwarm", as_cmap=True)

    #time
    time = da.time.data
    #altitude
    if zref.upper()=='AGL':
        altitude = da.altitude.data - da.station_altitude.data
    elif zref.upper()=='ASL':
        altitude = da.altitude.data

    #2D array
    C = np.transpose(da[var].data)


    fig, axs = plt.subplots(1, 1, figsize=(12, 4))

    if log:
        import matplotlib.colors as colors
        plt.pcolormesh(time, altitude, C, norm=colors.LogNorm(vmin=np.max([1e0,vmin]), vmax=vmax), cmap=cmap, shading='nearest')
    else:
        plt.pcolormesh(time, altitude, C, vmin=vmin, vmax=vmax, cmap=cmap, shading='nearest')

    #add addition information
    if show_fog:
        _plot_fog(da, zref)
    if show_clouds:
        _plot_clouds(da, zref)
    if show_pbl:
        _plot_pbl(da, zref)

    #limit to altitude range
    plt.ylim([zmin,zmax])

    #set title and axis labels
    yyyy = pd.to_datetime(da.time.values[0]).year
    mm = pd.to_datetime(da.time.values[0]).month
    dd = pd.to_datetime(da.time.values[0]).day
    latitude = da.station_latitude.data
    longitude = da.station_longitude.data
    altitude = da.station_altitude.data
    station_id = da.attrs['site_location']
    #title
    plt.title('{} ({:.2f};{:.2f};{:.1f}m) - {}/{:02}/{:02}'.format(station_id, latitude, longitude, altitude, yyyy, mm, dd), weight='bold')
    #labels
    plt.xlabel('Time')
    plt.ylabel('Altitude {} (m)'.format(zref.upper()))

    #add legend
    if show_fog or show_clouds or show_pbl:
        plt.legend(loc='upper right')

    #colorbar
    cbar = plt.colorbar()
    #label
    if 'units' in list(da[var].attrs) and da[var].units!=None:
        label = '{} ({})'.format(da[var].long_name, da[var].units)
    else:
        label = '{}'.format(da[var].long_name)
    cbar.set_label(label)

    plt.tight_layout()
    plt.show()
