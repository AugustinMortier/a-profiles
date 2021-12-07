# @author Augustin Mortier
# @desc A-Profiles - Image plot

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import seaborn as sns

sns.set_theme()


def _plot_foc(da, zref):
    """Plot foc at the bottom of the image
    Args:
        da ([type]): [description]
    """
    # time
    time = da.time.data
    # altitude
    if zref.upper() == "AGL":
        altitude = da.altitude.data - da.station_altitude.data
    elif zref.upper() == "ASL":
        altitude = da.altitude.data
    
    foc_markers = [altitude[0] if x else np.nan for x in da.foc.data]

    # plot line from peak to base
    for i, _ in enumerate(foc_markers):
        if not np.isnan(foc_markers[i]):
            plt.plot(
                [time[i], time[i]],
                [altitude[0], altitude[-1]],
                "-",
                color="black",
                lw=2.0,
                alpha=0.4,
            )
    # plot markers
    plt.plot([], [], "^m", ms=10, lw=0, label="fog or condensation")
    plt.plot(time, foc_markers, "m", marker=10, ms=10, lw=0)


def _plot_clouds(da, zref):
    """Plot clouds as markers.
    Args:
        da ([type]): [description]
    """
    # time
    time = da.time.data
    # altitude
    if zref.upper() == "AGL":
        altitude = da.altitude.data - da.station_altitude.data
    elif zref.upper() == "ASL":
        altitude = da.altitude.data

    for i in range(len(time)):
        # plot bases
        b_indexes = [i for i, x in enumerate(da.clouds_bases[i, :].data) if x]
        p_indexes = [i for i, x in enumerate(da.clouds_peaks[i, :].data) if x]
        t_indexes = [i for i, x in enumerate(da.clouds_tops[i, :].data) if x]

        # plot line from base to peak
        for j, _ in enumerate(b_indexes):
            y = altitude[b_indexes[j]: p_indexes[j]]
            x = [time[i] for _ in y]
            plt.plot(x, y, "w-", lw=2.0, alpha=0.2)

        # plot line from peak to base
        for j, _ in enumerate(b_indexes):
            y = altitude[p_indexes[j]: t_indexes[j]]
            x = [time[i] for _ in y]
            plt.plot(x, y, "w-", lw=2.0, alpha=0.2)

        """
        #plot line from base to top
        for j, _ in enumerate(b_indexes):
            y = altitude[b_indexes[j]:t_indexes[j]]
            x = [time[i] for _ in y]
            plt.plot(x, y, 'w-', lw=2, alpha=0.9)
        """
        # plot markers
        t = [time[i] for _ in b_indexes]
        if i == 0:
            plt.plot(t, altitude[b_indexes], "k.", ms=3, label="clouds")
        else:
            plt.plot(t, altitude[b_indexes], "k.", ms=3)
        t = [time[i] for _ in p_indexes]
        plt.plot(t, altitude[p_indexes], "k.", ms=3)
        t = [time[i] for _ in t_indexes]
        plt.plot(t, altitude[t_indexes], "k.", ms=3)


def _plot_pbl(da, zref):
    """Plot PBL as markers
    Args:
        da ([type]): [description]
    """
    # time
    time = da.time.data
    # altitude
    if zref.upper() == "AGL":
        pbl = da.pbl.data - da.station_altitude.data
    elif zref.upper() == "ASL":
        pbl = da.pbl.data
    plt.plot(time, pbl, ".g", ms=5, lw=0, label="PBL")


def plot(
    da,
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
    cmap="coolwarm",
    show_fig=True,
    save_fig = None
):
    """Plot image of selected variable from :class:`aprofiles.profiles.ProfilesData` object.

    Args:
        - da (:class:`xarray.DataArray`): DataArray.
        - var (str, optional): Variable of the DataArray to be plotted. Defaults to `'attenuated_backscatter_0'`.
        - zref ({'agl', 'asl'},optional): Base reference for altitude axis. Defaults to 'agl'.
        - zmin (float, optional): Minimum altitude AGL (m). Defaults to minimum available altitude.
        - zmax (float, optional): Maximum altitude AGL (m). Defaults to maximum available altitude.
        - vmin (float, optional): Minimum value. Defaults to `None`.
        - vmax (float, optional): Maximum value. If None, calculates max from data.
        - log (bool, optional), Use logarithmic scale. Defaults to `None`.
        - show_foc (bool, optional): Add foc detection. Defaults to `False`.
        - show_pbl (bool, optional): Add PBL height. Defaults to `False`.
        - show_clouds (bool, optional): Add clouds detection. Defaults to `False`.
        - cmap (str, optional): Matplotlib colormap. Defaults to `'coolwarm'` cmap from seaborn.
        - show_fig (bool, optional): Show Figure. Defaults to `True`.
        - save_fig (str, optional): Path of the saved figure. Defaults to `None`.

    Example:
        >>> import aprofiles as apro
        >>> # read example file
        >>> path = "examples/data/L2_0-20000-001492_A20210909.nc"
        >>> reader = apro.reader.ReadProfiles(path)
        >>> profiles = reader.read()
        >>> # attenuated backscatter image
        >>> profiles.plot(vmin=1e-2, vmax=1e1, log=True)

        .. figure:: ../../docs/_static/images/attenuated_backscatter.png
            :scale: 50 %
            :alt: attenuated backscatter profiles

            Image of attenuated backscatter profiles.
    """

    # calculates max value from data
    if vmax is None:
        perc = np.percentile(da[var].data, 70)
        pow10 = np.ceil(np.log10(perc))
        vmax = 10 ** (pow10)

    # time
    time = da.time.data
    # altitude
    if zref.upper() == "AGL":
        altitude = da.altitude.data - da.station_altitude.data
    elif zref.upper() == "ASL":
        altitude = da.altitude.data

    fig, axs = plt.subplots(1, 1, figsize=(12, 4))

    # 2D array
    C = np.transpose(da[var].data)

    if log:
        import matplotlib.colors as colors

        plt.pcolormesh(
            time,
            altitude,
            C,
            norm=colors.LogNorm(vmin=np.max([0, vmin]), vmax=vmax),
            cmap=cmap,
            shading="nearest",
        )
    else:
        plt.pcolormesh(
            time, altitude, C, vmin=vmin, vmax=vmax, cmap=cmap, shading="nearest"
        )

    # add addition information
    if show_foc:
        _plot_foc(da, zref)
    if show_clouds:
        _plot_clouds(da, zref)
    if show_pbl:
        _plot_pbl(da, zref)

    # limit to altitude range
    plt.ylim([zmin, zmax])

    # set title and axis labels
    yyyy = pd.to_datetime(da.time.values[0]).year
    mm = pd.to_datetime(da.time.values[0]).month
    dd = pd.to_datetime(da.time.values[0]).day
    latitude = da.station_latitude.data
    longitude = da.station_longitude.data
    altitude = da.station_altitude.data
    station_id = da.attrs["site_location"]
    # title
    plt.title(
        f"{station_id} ({latitude:.2f};{longitude:.2f};{altitude:.1f}m) - {yyyy}/{mm:02}/{dd:02}",
        weight="bold",
    )
    # labels
    plt.xlabel("Time")
    plt.ylabel(f"Altitude {zref.upper()} (m)")

    # add legend
    if show_foc or show_clouds or show_pbl:
        plt.legend(loc="upper right")

    # colorbar
    cbar = plt.colorbar()
    # label
    if "units" in list(da[var].attrs) and da[var].units is not None:
        label = f"{da[var].long_name} ({da[var].units})"
    else:
        label = f"{da[var].long_name}"
    cbar.set_label(label)

    plt.tight_layout()
    if save_fig:
        plt.savefig(save_fig)
    if show_fig:
        plt.show()