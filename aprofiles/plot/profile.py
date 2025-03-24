# @author Augustin Mortier
# @desc A-Profiles - Single profile plot

import matplotlib.pyplot as plt
import numpy as np

import seaborn as sns

sns.set_theme()


def _plot_foc(da, time, zref):
    """Plot foc at the bottom of the image
    Args:
        da ([type]): [description]
        time ([type]): time for which to plot the foc
    """
    # time
    da_time = da.time.data
    i_time = np.argmin(abs(da_time - time))
    # altitude
    if zref.upper() == "AGL":
        altitude = da.altitude.data
    elif zref.upper() == "ASL":
        altitude = da.altitude.data + da.station_altitude.data[i_time]

    foc_markers = [altitude[0] if x else np.nan for x in da.foc.data]
    if not np.isnan(foc_markers[i_time]):
        plt.plot([], [], "^m", ms=10, lw=0, label="fog or condensation")
        plt.plot(0, foc_markers[i_time], "m", marker=10, ms=10, lw=0)


def _plot_clouds(da, time, var, zref):
    """Plot clouds layers
    Args:
        da ([type]): [description]
        time ([type]): time for which to plot the clouds
    """
    # time
    da_time = da.time.data
    i_time = np.argmin(abs(da_time - time))
    # altitude
    if zref.upper() == "AGL":
        altitude = da.altitude.data
    elif zref.upper() == "ASL":
        altitude = da.altitude.data + da.station_altitude.data[i_time]

    c_indexes = da.clouds.data[i_time, :]
    if not np.isnan(da.clouds.data[i_time]).all():
        # plt.plot([], [], "^m", ms=10, lw=0, label=f'Clouds ({da.clouds.method})')
        plt.plot(
            da[var].data[i_time, c_indexes],
            altitude[c_indexes],
            "m",
            marker=10,
            ms=6,
            lw=0,
            label=f"clouds ({da.clouds.method})",
        )


def _plot_pbl(da, time, var, zref):
    """Plot planetary boundary layer
    Args:
        da ([type]): [description]
        time ([type]): time for which to plot the clouds
    """

    # time
    da_time = da.time.data
    i_time = np.argmin(abs(da_time - time))
    # altitude
    if zref.upper() == "AGL":
        altitude = da.altitude.data
    elif zref.upper() == "ASL":
        altitude = da.altitude.data + da.station_altitude.data[i_time]

    # get index of pbl
    i_pbl = np.argmin(abs(da.altitude.data - da.pbl.data[i_time]))

    # plot pbl
    plt.plot(da[var].data[i_time, i_pbl], altitude[i_pbl], "gX", label="PBL")


def plot(
    da,
    datetime,
    var="attenuated_backscatter_0",
    zref="agl",
    zmin=None,
    zmax=None,
    vmin=None,
    vmax=None,
    log=False,
    show_foc=False,
    show_pbl=False,
    show_clouds=False,
    show_fig=True,
    save_fig=None,
):
    """
    Plot single profile of selected variable from (aprofiles.profiles.ProfilesData): object.

    Args:
        da (xarray.DataArray): DataArray.
        datetime (numpy.datetime64): Time for which the profile is plotted.
        var (str, optional): Variable of the DataArray to be plotted.
        zref ({'agl', 'asl'}, optional): Base reference for the altitude axis. Defaults to 'agl'.
        zmin (float, optional): Minimum altitude AGL (m). Defaults to minimum available altitude.
        zmax (float, optional): Maximum altitude AGL (m). Defaults to maximum available altitude.
        vmin (float, optional): Minimum value.
        vmax (float, optional): Maximum value. If None, calculates max from data.
        log (bool, optional): Use logarithmic scale.
        show_foc (bool, optional): Add foc detection.
        show_pbl (bool, optional): Add PBL height.
        show_clouds (bool, optional): Add clouds detection.
        show_fig (bool, optional): Show figure.
        save_fig (str, optional): Path of the saved figure.

    Example:
        ```python
        import aprofiles as apro
        # read example file
        path = "examples/data/L2_0-20000-001492_A20210909.nc"
        reader = apro.reader.ReadProfiles(path)
        profiles = reader.read()
        # some detection
        profiles.clouds(inplace=True).pbl(inplace=True)
        # attenuated backscatter single profile
        datetime = np.datetime64('2021-09-09T10:25:00')
        profiles.plot(datetime=datetime, vmin=-1, vmax=10, zmax=12000, show_clouds=True, show_pbl=True)
        ```

        ![Single profile of attenuated backscatter](../../assets/images/Profile-Oslo-20210909T212005.png){: style="width: 60%;" }
    """

    if datetime is None:
        raise ValueError(
            "datetime needs to be a np.datetime object, e.g. time=np.datetime(2021-09-09T16:00:00)"
        )
    # get index of closest profile
    da_time = da.time.data
    i_time = np.argmin(abs(da_time - datetime))

    # altitude
    if zref.upper() == "AGL":
        altitude = da.altitude.data
    elif zref.upper() == "ASL":
        altitude = da.altitude.data + da.station_altitude.data[i_time]

    fig, axs = plt.subplots(1, 1, figsize=(6, 6))
    plt.plot(da[var].data[i_time], altitude)
    # add zeros
    plt.plot(np.zeros(len(altitude)), altitude, ":k", alpha=0.2)

    if log:
        axs.set_xscale("log")

    # add addition information
    if show_foc:
        _plot_foc(da, da_time[i_time], zref)
    if show_clouds:
        _plot_clouds(da, da_time[i_time], var, zref)
    if show_pbl:
        _plot_pbl(da, da_time[i_time], var, zref)

    # set scales
    plt.ylim([zmin, zmax])
    if vmin is not None or vmax is not None:
        plt.xlim([vmin, vmax])

    # set title and axis labels
    latitude = da.station_latitude.data[i_time]
    longitude = da.station_longitude.data[i_time]
    altitude = da.station_altitude.data[i_time]
    station_id = da.attrs["site_location"]
    # title
    plt.title(
        f"{station_id} ({latitude:.2f};{longitude:.2f};{altitude:.1f}m) - {np.datetime_as_string(da_time[i_time]).split('.')[0]}",
        weight="bold",
        fontsize=12,
    )
    # labels
    if "units" in list(da[var].attrs) and da[var].units is not None:
        xlabel = f"{da[var].long_name} ({da[var].units})"
    else:
        xlabel = f"{da[var].long_name}"
    plt.xlabel(xlabel)
    plt.ylabel(f"Altitude {zref.upper()} (m)")

    # add legend
    if show_foc or show_clouds or show_pbl:
        plt.legend(loc="upper right")

    plt.tight_layout()
    if save_fig:
        plt.savefig(save_fig)
    if show_fig:
        plt.show()
