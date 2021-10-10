#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles - Single profile plot

import matplotlib.pyplot as plt
import numpy as np

import seaborn as sns
sns.set_theme()


def _plot_fog(da, time, zref):
    """Plot fog at the bottom of the image
    Args:
        da ([type]): [description]
        time ([type]): time for which to plot the fog
    """
    #time
    da_time = da.time.data
    i_time = np.argmin(abs(da_time-time))
    #altitude
    if zref.upper()=='AGL':
        altitude = da.altitude.data - da.station_altitude.data
    elif zref.upper()=='ASL':
        altitude = da.altitude.data

    fog_markers = [altitude[0] if x==True else np.nan for x in da.foc.data]
    if not np.isnan(fog_markers[i_time]):
        plt.plot([],[],"^m", ms=10, lw=0, label='fog or condensation')
        plt.plot(0, fog_markers[i_time],"m", marker=10, ms=10, lw=0)

def _plot_clouds(da, time, var, zref):
    """Plot clouds layers
    Args:
        da ([type]): [description]
        time ([type]): time for which to plot the clouds
    """
    #time
    da_time = da.time.data
    i_time = np.argmin(abs(da_time-time))
    #altitude
    if zref.upper()=='AGL':
        altitude = da.altitude.data - da.station_altitude.data
    elif zref.upper()=='ASL':
        altitude = da.altitude.data

    #plot bases
    b_indexes = [i for i, x in enumerate(da.clouds_bases[i_time,:].data) if x]
    plt.plot(da[var].data[i_time,b_indexes], altitude[b_indexes], 'k.')

    #plot peaks
    p_indexes = [i for i, x in enumerate(da.clouds_peaks[i_time,:].data) if x]
    plt.plot(da[var].data[i_time,p_indexes], altitude[p_indexes], 'k.')
    
    #plot tops
    t_indexes = [i for i, x in enumerate(da.clouds_tops[i_time,:].data) if x]
    plt.plot(da[var].data[i_time,t_indexes], altitude[t_indexes], 'k.')

    #plot some pretty lines around each cloud
    for i, _ in enumerate(b_indexes):
        #bottom line
        if i==0:
            plt.plot([da[var].data[i_time,b_indexes[i]], da[var].data[i_time,p_indexes[i]]],[altitude[b_indexes[i]], altitude[b_indexes[i]]],':k', label='cloud layer')
        else:
            plt.plot([da[var].data[i_time,b_indexes[i]], da[var].data[i_time,p_indexes[i]]],[altitude[b_indexes[i]], altitude[b_indexes[i]]],':k')
        #top line
        plt.plot([da[var].data[i_time,t_indexes[i]], da[var].data[i_time,p_indexes[i]]],[altitude[t_indexes[i]], altitude[t_indexes[i]]],':k')
        #vertical line
        plt.plot([da[var].data[i_time,p_indexes[i]], da[var].data[i_time,p_indexes[i]]],[altitude[b_indexes[i]], altitude[t_indexes[i]]],':k')

def _plot_pbl(da, time, var, zref):
    """Plot planetary boundary layer
    Args:
        da ([type]): [description]
        time ([type]): time for which to plot the clouds
    """
    #time
    da_time = da.time.data
    i_time = np.argmin(abs(da_time-time))
    #altitude
    if zref.upper()=='AGL':
        pbl = da.pbl.data - da.station_altitude.data
    elif zref.upper()=='ASL':
        pbl = da.pbl.data
    
    #get index of pbl
    i_pbl = np.argmin(abs(da.altitude.data-pbl[i_time]))

    #plot pbl
    plt.plot(da[var].data[i_time,i_pbl], pbl[i_time], 'gX', label='PBL')


def plot(da, datetime, var='attenuated_backscatter_0', zref='agl', zmin=None, zmax= None, vmin=None, vmax=None, log=False, show_fog=False, show_pbl=False, show_clouds=False):
    """Plot single profile of selected variable from :class: :ref:`ProfilesData` object.

    Args:
        - da (xr.DataArray): DataArray.
        - datetime (np.datetime64): time for which we plot the profile.
        - var (str, optional): Variable of the DataArray to be plotted. Defaults to 'attenuated_backscatter_0'.
        - zref (str,optional): Base for altitude. Expected values: 'agl' (above ground level) or 'asl' (above sea level). Defaults to 'agl'.
        - zmin (float, optional): Minimum altitude AGL (m). Defaults to minimum available altitude.
        - zmax (float, optional): Maximum altitude AGL (m). Defaults to maximum available altitude.
        - vmin (float, optional): Minimum value. Defaults to 0.
        - vmax (float, optional): Maximum value. If None, calculates max from data.
        - log (bool, optional), Use logarithmic scale. Defaults to None.
        - show_fog (bool, optional): Add fog detection. Defaults to False.
        - show_pbl (bool, optional): Add PBL height. Defaults to False.
        - show_clouds (bool, optional): Add clouds detection. Defaults to False.
    """

    if datetime==None:
        raise ValueError("datetime needs to be a np.datetime object, e.g. time=np.datetime(2021-09-09T16:00:00)")
    #get index of closest profile
    da_time = da.time.data
    i_time = np.argmin(abs(da_time-datetime))

    #altitude
    if zref.upper()=='AGL':
        altitude = da.altitude.data - da.station_altitude.data
    elif zref.upper()=='ASL':
        altitude = da.altitude.data
    
    fig, axs = plt.subplots(1, 1, figsize=(6, 6))
    plt.plot(da[var].data[i_time], altitude)
    #add zeros
    plt.plot(np.zeros(len(altitude)), altitude, ':k', alpha=0.2)

    if log:
        axs.set_xscale('log')

    #add addition information
    if show_fog:
        _plot_fog(da, da_time[i_time], zref)
    if show_clouds:
        _plot_clouds(da, da_time[i_time], var, zref)
    if show_pbl:
        _plot_pbl(da, da_time[i_time], var, zref)
    

    #set scales
    plt.ylim([zmin, zmax])
    if vmin!=None or vmax!=None:
        plt.xlim([vmin, vmax])

    #set title and axis labels
    latitude = da.station_latitude.data
    longitude = da.station_longitude.data
    altitude = da.station_altitude.data
    station_id = da.attrs['site_location']
    #title
    plt.title('{} ({:.2f};{:.2f};{:.1f}m) - {}'.format(station_id, latitude, longitude, altitude, np.datetime_as_string(da_time[i_time]).split('.')[0]), weight='bold', fontsize=12)
    #labels
    if 'units' in list(da[var].attrs) and da[var].units!=None:
        xlabel = '{} ({})'.format(da[var].long_name.replace('wavelength 0',str(da.l0_wavelength.data)), da[var].units)
    else:
        xlabel = '{}'.format(da[var].long_name.replace('wavelength 0',str(da.l0_wavelength.data)))
    plt.xlabel(xlabel)
    plt.ylabel('Altitude {} (m)'.format(zref.upper()))

    #add legend
    if show_fog or show_clouds or show_pbl:
        plt.legend(loc='upper right')

    plt.tight_layout()
    plt.show()
