#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles - Single profile plot

import matplotlib.pyplot as plt
import numpy as np


def _plot_fog(da, time):
    """Plot fog at the bottom of the image
    Args:
        da ([type]): [description]
        time ([type]): time for which to plot the fog
    """
    da_time = da.time.data
    itime = np.argmin(abs(da_time-time))

    fog_markers = [1 if x==True else False for x in da.fog_or_condensation.data]
    if fog_markers[itime]:
        plt.plot(fog_markers[itime], 0,"^:m",ms=10,lw=0, label='fog or condensation')

def _plot_clouds(da, time, var, altitude):
    """Plot clouds layers
    Args:
        da ([type]): [description]
        time ([type]): time for which to plot the clouds
    """
    da_time = da.time.data
    itime = np.argmin(abs(da_time-time))

    #plot bases
    b_indexes = [i for i, x in enumerate(da.clouds_bases[itime,:].data) if x]
    plt.plot(da[var].data[itime,b_indexes], altitude[b_indexes], 'k.')

    #plot peaks
    p_indexes = [i for i, x in enumerate(da.clouds_peaks[itime,:].data) if x]
    plt.plot(da[var].data[itime,p_indexes], altitude[p_indexes], 'k.')
    
    #plot tops
    t_indexes = [i for i, x in enumerate(da.clouds_tops[itime,:].data) if x]
    plt.plot(da[var].data[itime,t_indexes], altitude[t_indexes], 'k.')

    #plot some pretty lines around each cloud
    for i, _ in enumerate(b_indexes):
        #bottom line
        if i==0:
            plt.plot([da[var].data[itime,b_indexes[i]], da[var].data[itime,p_indexes[i]]],[altitude[b_indexes[i]], altitude[b_indexes[i]]],':k', label='cloud layer')
        else:
            plt.plot([da[var].data[itime,b_indexes[i]], da[var].data[itime,p_indexes[i]]],[altitude[b_indexes[i]], altitude[b_indexes[i]]],':k')
        #top line
        plt.plot([da[var].data[itime,t_indexes[i]], da[var].data[itime,p_indexes[i]]],[altitude[t_indexes[i]], altitude[t_indexes[i]]],':k')
        #vertical line
        plt.plot([da[var].data[itime,p_indexes[i]], da[var].data[itime,p_indexes[i]]],[altitude[b_indexes[i]], altitude[t_indexes[i]]],':k')
    


def plot(da, time, var='attenuated_backscatter_0', zmin=None, zmax= None, vmin=None, vmax=None, log=False, show_fog=False, show_pbl=False, show_clouds=False):
    """Plot image of profiles.

    Args:
        da (xr.DataArray): DataArray.
        time (np.datetime64): time for which we plot the profile.
        var (str, optional): Variable of the DataArray to be plotted. Defaults to 'attenuated_backscatter_0'.
        zmin (float, optional): Minimum altitude AGL (m). Defaults to minimum available altitude.
        zmax (float, optional): Maximum altitude AGL (m). Defaults to maximum available altitude.
        vmin (float, optional): Minimum value. Defaults to 0.
        vmax (float, optional): Maximum value. If None, calculates max from data.
        log (bool, optional), Use logarithmic scale. Defaults to None.
        show_fog (bool, optional): Add fog detection. Defaults to False.
        show_pbl (bool, optional): Add PBL height. Defaults to False.
        show_clouds (bool, optional): Add clouds detection. Defaults to False.
    """

    if time==None:
        raise ValueError("time needs to be a np.datetime object, e.g. time=np.datetime(2021-09-09T16:00:00)")
    #get index of closest profile
    da_time = da.time.data
    itime = np.argmin(abs(da_time-time))

    #altitude AGL
    altitude = da.altitude.data - da.station_altitude.data
    
    fig, axs = plt.subplots(1, 1, figsize=(6, 6))
    plt.plot(da[var].data[itime], altitude)

    if log:
        axs.set_xscale('log')

    #add addition information
    if show_fog:
        _plot_fog(da, da_time[itime])
    if show_clouds:
        _plot_clouds(da, da_time[itime], var, altitude)

    #set scales
    plt.ylim([zmin, zmax])
    if vmin!=None and vmax!=None:
        plt.xlim([vmin, vmax])

    #set title and axis
    latitude = da.station_latitude.data
    longitude = da.station_longitude.data
    altitude = da.station_altitude.data
    station_id = da.attrs['site_location']
    plt.title('{} ({:.2f};{:.2f}) - Alt: {} m - {}'.format(station_id, latitude, longitude, altitude, np.datetime_as_string(da_time[itime]).split('.')[0]), weight='bold', fontsize=10)
    plt.xlabel(da[var].long_name)
    plt.ylabel('Altitude AGL (m)')

    #add legend
    if show_fog or show_clouds or show_pbl:
        plt.legend(loc='upper right')

    plt.tight_layout()
    plt.show()
