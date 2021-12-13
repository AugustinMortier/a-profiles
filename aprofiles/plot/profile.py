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
        altitude = da.altitude.data - da.station_altitude.data
    elif zref.upper() == "ASL":
        altitude = da.altitude.data

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
        altitude = da.altitude.data - da.station_altitude.data
    elif zref.upper() == "ASL":
        altitude = da.altitude.data

    # plot bases
    b_indexes = [i for i, x in enumerate(da.clouds_bases[i_time, :].data) if x]
    plt.plot(da[var].data[i_time, b_indexes], altitude[b_indexes], "k.")

    # plot peaks
    p_indexes = [i for i, x in enumerate(da.clouds_peaks[i_time, :].data) if x]
    plt.plot(da[var].data[i_time, p_indexes], altitude[p_indexes], "k.")

    # plot tops
    t_indexes = [i for i, x in enumerate(da.clouds_tops[i_time, :].data) if x]
    plt.plot(da[var].data[i_time, t_indexes], altitude[t_indexes], "k.")

    # plot some pretty lines around each cloud
    for i, _ in enumerate(b_indexes):
        # bottom line
        if i == 0:
            plt.plot(
                [
                    da[var].data[i_time, b_indexes[i]],
                    da[var].data[i_time, p_indexes[i]],
                ],
                [altitude[b_indexes[i]], altitude[b_indexes[i]]],
                ":k",
                label="cloud layer",
            )
        else:
            plt.plot(
                [
                    da[var].data[i_time, b_indexes[i]],
                    da[var].data[i_time, p_indexes[i]],
                ],
                [altitude[b_indexes[i]], altitude[b_indexes[i]]],
                ":k",
            )
        # top line
        plt.plot(
            [da[var].data[i_time, t_indexes[i]], da[var].data[i_time, p_indexes[i]]],
            [altitude[t_indexes[i]], altitude[t_indexes[i]]],
            ":k",
        )
        # vertical line
        plt.plot(
            [da[var].data[i_time, p_indexes[i]], da[var].data[i_time, p_indexes[i]]],
            [altitude[b_indexes[i]], altitude[t_indexes[i]]],
            ":k",
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
        altitude = da.altitude.data - da.station_altitude.data
    elif zref.upper() == "ASL":
        altitude = da.altitude.data

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
    save_fig=None
):
    """Plot single profile of selected variable from :class:`aprofiles.profiles.ProfilesData` object.

    Args:
        - da (:class:`xarray.DataArray`): DataArray.
        - datetime (:class:`numpy.datetime64`): time for which we plot the profile.
        - var (str, optional): Variable of the DataArray to be plotted. Defaults to `'attenuated_backscatter_0'`.
        - zref ({'agl', 'asl'},optional): Base reference for altitude axis. Defaults to 'agl'.
        - zmin (float, optional): Minimum altitude AGL (m). Defaults to minimum available altitude.
        - zmax (float, optional): Maximum altitude AGL (m). Defaults to maximum available altitude.
        - vmin (float, optional): Minimum value. Defaults to `0`.
        - vmax (float, optional): Maximum value. If None, calculates max from data.
        - log (bool, optional), Use logarithmic scale. Defaults to `None`.
        - show_foc (bool, optional): Add foc detection. Defaults to `False`.
        - show_pbl (bool, optional): Add PBL height. Defaults to `False`.
        - show_clouds (bool, optional): Add clouds detection. Defaults to `False`.
        - show_fig (bool, optional): Show Figure. Defaults to `True`.
        - save_fig (str, optional): Path of the saved figure. Defaults to `None`.

    Example:
        >>> import aprofiles as apro
        >>> # read example file
        >>> path = "examples/data/L2_0-20000-001492_A20210909.nc"
        >>> reader = apro.reader.ReadProfiles(path)
        >>> profiles = reader.read()
        >>> # some detection
        >>> profiles.clouds(inplace=True).pbl(inplace=True)
        >>> # attenuated backscatter single profile
        >>> datetime = np.datetime64('2021-09-09T10:25:00')
        >>> profiles.plot(datetime=datetime, vmin=-1, vmax=10, zmax=12000, show_clouds=True, show_pbl=True)

        .. figure:: ../../docs/_static/images/Profile-Oslo-20210909T212005.png
            :scale: 80 %
            :alt: profile

            Single profile of attenuated backscatter.
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
        altitude = da.altitude.data - da.station_altitude.data
    elif zref.upper() == "ASL":
        altitude = da.altitude.data

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
    latitude = da.station_latitude.data
    longitude = da.station_longitude.data
    altitude = da.station_altitude.data
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

