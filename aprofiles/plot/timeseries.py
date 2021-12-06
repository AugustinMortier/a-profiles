# @author Augustin Mortier
# @desc A-Profiles - Time Series plot

import matplotlib.pyplot as plt
import pandas as pd

import seaborn as sns

sns.set_theme()


def plot(da, var="aod", show_fig=True, save_fig=None, **kwargs):
    """Plot time series of selected variable from :class:`aprofiles.profiles.ProfilesData` object.

    Args:
        - da (:class:`xarray.DataArray`): DataArray
        - var (str, optional): [description]. Defaults to `'aod'`.
        - show_fig (bool, optional): Show Figure. Defaults to `True`.
        - save_fig (str, optional): Path of the saved figure. Defaults to `None`.

    Example:

        >>> import aprofiles as apro
        >>> # read example file
        >>> path = "examples/data/L2_0-20000-001492_A20210909.nc"
        >>> reader = apro.reader.ReadProfiles(path)
        >>> profiles = reader.read()
        >>> # retrieve pbl height
        >>> profiles.pbl(zmin=200, zmax=3000)
        >>> # attenuated backscatter image
        >>> profiles.plot(var="pbl" ymin=0., ymax=3000., min_snr=2.)

        .. figure:: ../../docs/_static/images/time_series.png
            :scale: 50 %
            :alt: time series

            Time series of Planetary Boundary Layer height.
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
    plt.title(
        f"{station_id} ({latitude:.2f};{longitude:.2f};{altitude:.1f}m) - {yyyy}/{mm:02}/{dd:02}",
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
