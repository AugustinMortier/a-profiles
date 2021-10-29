#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles - Profiles writing method

import copy
import os
import warnings

import xarray as xr


def write(profiles, base_dir, verbose):
    """Writing method for an instance of a :class:`aprofiles.profiles.ProfilesData` class.

    Args:
        - aprofiles (:class:`aprofiles.profiles.ProfilesData`): Object to be written.
        - base_dir (str): Base path of the file should be written.
        - verbose (bool): Verbose mode. Defaults to False.
    """    

    def _file_exists(path):
        return os.path.exists(path)
    
    def _convert_time_after_epoch(ds, resolution='ms'):
        time_attrs = ds["time"].attrs
        ds = ds.assign_coords(time=ds.time.data.astype(f"datetime64[{resolution}]").astype(int))
        ds["time"] = ds["time"].assign_attrs(time_attrs)
        ds["time"].attrs['units'] = 'milliseconds after epoch'
        return ds
    
    def _classify_scene(ds):
        lowest_clouds = profiles._get_lowest_clouds()
        scene = []
        # got clouds classification here: https://www.metoffice.gov.uk/weather/learn-about/weather/types-of-weather/clouds
        for i, lowest_cloud in enumerate(lowest_clouds):
            if lowest_cloud<=1981:
                scene.append('low_cloud')
            elif lowest_cloud>1981 and lowest_cloud<=6096:
                scene.append('mid_cloud')
            elif lowest_cloud>6096:
                scene.append('high_cloud')
            else:
                scene.append('aer')
            # overwrite result based on foc
            if ds.foc.data[i]:
                scene[i] = 'foc'
        return scene

    # get dataset from profilesdata
    dataset = profiles.data

    #get date as string yyyy-mm-dd from first value of the time data
    str_date = str(dataset.time.values[0])[:10]
    yyyy = str_date[:4]
    mm = str_date[5:7]
    dd = str_date[8:10]
    filename = f"{dataset.wigos_station_id}-{str_date}.nc"
    path = os.path.join(base_dir, yyyy, mm, dd, 'profiles', filename)

    if _file_exists(path) and verbose:
        warnings.warn(f"{path} already exists and will be overwritten.")
    else:
        from pathlib import Path
        Path(os.path.join(base_dir, yyyy, mm, dd, 'profiles')).mkdir(parents=True, exist_ok=True)

    # creates a copy od original dataset -> writes only necessary data
    ds = copy.deepcopy(dataset)

    # for the mass concentration, we just need the emc.
    emc = {}
    for data_var in list(ds.data_vars):
        if 'mass_concentration:' in data_var:
            emc[data_var.split(':')[1]] = dataset[data_var].emc
            ds = ds.drop(data_var)

    # add emc as new dataarray
    ds["emc"] = xr.DataArray(
        data=list(emc.values()),
        dims=["aer_type"],
        coords=dict(
            aer_type=list(emc.keys()),
        ),
        attrs=dict(long_name="Extinction to Mass Coefficient", units='m2.g-1'),
    )
    # add attributes to aer_type
    ds["aer_type"] = ds["aer_type"].assign_attrs({
        'long_name': 'Aerosol type'
    })

    # determines the scene classification for each profile
    scene = _classify_scene(ds)
    # add scene as new dataarray
    ds["scene"] = ("time", scene)
    ds["scene"] = ds["scene"].assign_attrs({
        'long_name': "Scene classification",
        'definition': 'low-cloud: base cloud below 1981 m - mid_cloud: base cloud between 1981 m and 6096 m - high_cloud: base cloud above 6096 m - foc: fog or condensation'
    })

    # drop other variables
    drop_variables = ['cloud_base_height', 'vertical_visibility', 'cbh_uncertainties', 'uncertainties_att_backscatter_0']
    for drop_var in drop_variables:
        ds = ds.drop(drop_var)
    
    # some variables have no dimension. Set it as attribute and drop the variable.
    nodim_variables = ['l0_wavelength', 'station_latitude', 'station_longitude', 'station_altitude']
    for nodim_var in nodim_variables:
        ds.attrs[nodim_var] = ds[nodim_var].data
        ds = ds.drop(nodim_var)

    # converts time
    ds = _convert_time_after_epoch(ds, resolution='ms')

    # writes to netcdf
    ds.to_netcdf(path, mode='w')

