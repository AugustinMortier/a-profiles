# @author Augustin Mortier
# @desc A-Profiles - Time Series plot

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import seaborn as sns

sns.set_theme()


def plot(da, var="aod", show_fig=True, save_fig=None, **kwargs):
    """
    Plot time series of selected variable from (aprofiles.profiles.ProfilesData): object.

    Args:
        da (xarray.DataArray): DataArray
        var (str, optional): Variable of the DataArray to be plotted.
        show_fig (bool, optional): Show Figure.
        save_fig (str, optional): Path of the saved figure.

    Example:
        ``` python
        import aprofiles as apro
        # read example file
        path = "examples/data/L2_0-20000-001492_A20210909.nc"
        reader = apro.reader.ReadProfiles(path)
        profiles = reader.read()
        # retrieve pbl height
        profiles.pbl(zmin=200, zmax=3000)
        # attenuated backscatter image
        profiles.plot(var="pbl" ymin=0., ymax=3000., min_snr=2.)
        ```

        ![Time series of Planetary Boundary Layer height](../../assets/images/time_series.png)
    """

    def __init__(self):
        pass

    # get kwargs
    ymin = kwargs.get("ymin", None)
    ymax = kwargs.get("ymax", None)

    # time
    time = da.time.data

    fig, axs = plt.subplots(1, 1, figsize=(12, 4))

    # plot time series
    plt.plot(time, da[var].data)

    # limit to altitude range
    if ymin is not None or ymax is not None:
        plt.ylim([ymin, ymax])

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
    # title
    plt.title(
        f"{station_id} ({str_latitude};{str_longitude};{str_altitude}m) - {yyyy}/{mm:02}/{dd:02}",
        weight="bold",
    )
    # labels
    plt.xlabel("Time")

    if "units" in list(da[var].attrs) and da[var].units is not None:
        ylabel = f"{da[var].long_name} ({da[var].units})"
    else:
        ylabel = f"{da[var].long_name}"
    plt.ylabel(ylabel)

    plt.tight_layout()
    if save_fig:
        plt.savefig(save_fig)
    if show_fig:
        plt.show()
