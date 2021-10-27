#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles - Profiles writing method

import copy
import os
import warnings

import xarray as xr


def write(dataset, base_dir=''):
    """Writing method for an instance of a :class:`aprofiles.profiles.ProfilesData` class.

    Args:
        - dataset (:class:`xarray.DataArray`): Dataset to be written.
        - base_dir (str): Base path of the file should be written.
    """    

    def _file_exists(path):
        return os.path.exists(path)
    
    def _convert_time_after_epoch(ds, resolution='ms'):
        time_attrs = ds["time"].attrs
        ds = ds.assign_coords(time=ds.time.data.astype("datetime64[{}]".format(resolution)).astype(int))
        ds["time"] = ds["time"].assign_attrs(time_attrs)
        ds["time"].attrs['units'] = 'milliseconds after epoch'
        return ds

    #get date as string yyyy-mm-dd from first value of the time data
    str_date = str(dataset.time.values[0])[:10]
    yyyy = str_date[:4]
    mm = str_date[5:7]
    dd = str_date[8:10]
    filename = '{}-{}.nc'.format(dataset.wigos_station_id, str_date)
    path = os.path.join(base_dir, yyyy, mm, dd, filename)

    if _file_exists(path):
        warnings.warn('{} already exists and will be overwritten.'.format(path))
    else:
        from pathlib import Path
        Path(os.path.join(base_dir, yyyy, mm, dd)).mkdir(parents=True, exist_ok=True)

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

    # drop other variables
    drop_variables = ['cloud_base_height', 'vertical_visibility', 'cbh_uncertainties']
    for drop_var in drop_variables:
        ds = ds.drop(drop_var)

    # converts time
    ds = _convert_time_after_epoch(ds, resolution='ms')

    # writes to netcdf
    ds.to_netcdf(path, mode='w')

