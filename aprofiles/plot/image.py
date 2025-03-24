# @author Augustin Mortier
# @desc A-Profiles - Image plot

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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
        altitude = da.altitude.data
    else:
        raise ValueError("Unsupported altitude reference. Use 'AGL'.")

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
    """Plot clouds.
    Args:
        da ([type]): [description]
    """
    # time
    time = da.time.data
    clouds = da.clouds
    # altitude
    if zref.upper() == "AGL":
        altitude = da.altitude.data
    else:
        raise ValueError("Unsupported altitude reference. Use 'AGL'.")

    # 2D array
    C = np.transpose(clouds.data)
    C_plot = np.where(C, 1, np.nan)

    plt.pcolormesh(
        time,
        altitude,
        C_plot,
        shading="nearest",
        cmap="Greys_r",
        vmin=0,
        vmax=1,
        alpha=0.9,
    )

    # Manually create a legend entry
    plt.plot([], [], lw=0, marker="s", ms=10, color="white", alpha=0.9, label="clouds")


def _plot_pbl(da, zref):
    """Plot PBL as markers
    Args:
        da ([type]): [description]
    """
    # time
    time = da.time.data
    # altitude
    if zref.upper() == "AGL":
        pbl = da.pbl.data
    else:
        raise ValueError("Unsupported altitude reference. Use 'AGL'.")
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
    save_fig=None,
):
    """Plot image of selected variable from :class:`aprofiles.profiles.ProfilesData` object.

    Args:
        da (xarray.DataArray): DataArray.
        var (str, optional): Variable of the DataArray to be plotted.
        zref ({'agl'}, optional): Base reference for altitude axis.
        zmin (float, optional): Minimum altitude AGL (m).
        zmax (float, optional): Maximum altitude AGL (m).
        vmin (float, optional): Minimum value.
        vmax (float, optional): Maximum value. If `None`, calculates max from data.
        log (bool, optional): Use logarithmic scale.
        show_foc (bool, optional): Add foc detection.
        show_pbl (bool, optional): Add PBL height.
        show_clouds (bool, optional): Add clouds detection.
        cmap (str, optional): Matplotlib colormap.
        show_fig (bool, optional): Show figure.
        save_fig (str, optional): Path of the saved figure.

    Example:
        ``` python
        import aprofiles as apro
        # read example file
        path = "examples/data/L2_0-20000-001492_A20210909.nc"
        reader = apro.reader.ReadProfiles(path)
        profiles = reader.read()
        # attenuated backscatter image
        profiles.plot(vmin=1e-2, vmax=1e1, log=True)
        ```
        ![Image of attenuated backscatter profiles](../../assets/images/attenuated_backscatter.png)
    """

    # calculates max value from data
    if vmax is None and type(da[var].data[0][0]) != np.bool:
        perc = np.percentile(da[var].data, 70)
        pow10 = np.ceil(np.log10(perc))
        vmax = 10 ** (pow10)

    # time
    time = da.time.data
    # altitude
    if zref.upper() == "AGL":
        altitude = da.altitude.data
    else:
        raise ValueError("Unsupported altitude reference. Use 'AGL'.")

    fig, axs = plt.subplots(1, 1, figsize=(12, 4))

    # 2D array
    C = da[var].data.T

    if log:
        import matplotlib.colors as colors

        pcm = plt.pcolormesh(
            time,
            altitude,
            C,
            norm=colors.LogNorm(vmin=np.max([0, vmin]), vmax=vmax),
            cmap=cmap,
            shading="nearest",
        )
    else:
        pcm = plt.pcolormesh(
            time, altitude, C, vmin=vmin, vmax=vmax, cmap=cmap, shading="nearest"
        )
    # store colorbar
    cbar = fig.colorbar(pcm, ax=axs)

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
    str_latitude = (
        f"{latitude[0]:.2f}"
        if len(np.unique(latitude)) == 1
        else f"{np.min(latitude):.2f}-{np.max(latitude):.2f}"
    )
    str_longitude = (
        f"{longitude[0]:.2f}"
        if len(np.unique(longitude)) == 1
        else f"{np.min(longitude):.2f}-{np.max(longitude):.2f}"
    )
    str_altitude = (
        f"{altitude[0]:.2f}"
        if len(np.unique(altitude)) == 1
        else f"{np.min(altitude):.2f}-{np.max(altitude):.2f}"
    )

    plt.title(
        f"{station_id} ({str_latitude};{str_longitude};{str_altitude}m) - {yyyy}/{mm:02}/{dd:02}",
        weight="bold",
    )
    # labels
    plt.xlabel("Time")
    plt.ylabel(f"Altitude {zref.upper()} (m)")

    # add legend
    if show_foc or show_clouds or show_pbl:
        plt.legend(loc="upper right")

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
