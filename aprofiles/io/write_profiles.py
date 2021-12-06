# @author Augustin Mortier
# @desc A-Profiles - Profiles writing method

import copy
import os
import warnings

import numpy as np
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
                scene.append(3)
            elif lowest_cloud>1981 and lowest_cloud<=6096:
                scene.append(2)
            elif lowest_cloud>6096:
                scene.append(1)
            else:
                scene.append(0)
            # overwrite result based on foc
            if ds.foc.data[i]:
                scene[i] = 4
        return scene
    
    def _classify_retrieval_scene(ds):
        lowest_clouds = profiles._get_lowest_clouds()
        z_ref = profiles.data.z_ref.data
        scene = []
        for i, _ in enumerate(lowest_clouds):
            if lowest_clouds[i]>z_ref[i]:
                scene.append(1)
            elif lowest_clouds[i]<z_ref[i]:
                scene.append(3)
            else:
                scene.append(0)
            # overwrite result based on foc
            if ds.foc.data[i]:
                scene[i] = 4
        return scene

    # get dataset from profilesdata
    ds = profiles.data

    #get date as string yyyy-mm-dd from first value of the time data
    str_date = str(ds.time.values[0])[:10]
    yyyy = str_date[:4]
    mm = str_date[5:7]
    dd = str_date[8:10]
    filename = f"AP_{ds.wigos_station_id}-{ds.instrument_id}-{str_date}.nc"
    path = os.path.join(base_dir, yyyy, mm, dd, filename)

    if _file_exists(path) and verbose:
        warnings.warn(f"{path} already exists and will be overwritten.")
    else:
        from pathlib import Path
        Path(os.path.join(base_dir, yyyy, mm, dd)).mkdir(parents=True, exist_ok=True)

    # creates a copy od original dataset -> writes only necessary data
    ds_towrite = copy.deepcopy(ds)

    # for the mass concentration, we just need the emc.
    emc = {}
    for data_var in list(ds_towrite.data_vars):
        if 'mass_concentration:' in data_var:
            emc[data_var.split(':')[1]] = ds[data_var].emc
            ds_towrite = ds_towrite.drop(data_var)

    # add emc as new dataarray
    ds_towrite["emc"] = xr.DataArray(
        data=list(emc.values()),
        dims=["aer_type"],
        coords=dict(
            aer_type=list(emc.keys()),
        ),
        attrs=dict(long_name="Extinction to Mass Coefficient", units='m2.g-1', wavelength=ds.l0_wavelength.data),
    )
    # add attributes to aer_type
    ds_towrite["aer_type"] = ds_towrite["aer_type"].assign_attrs({
        'long_name': 'Aerosol type'
    })

    # determines the scene classification for each profile
    scene = _classify_scene(ds_towrite)
    # add scene as new dataarray
    ds_towrite["scene"] = ("time", scene)
    ds_towrite["scene"] = ds_towrite["scene"].assign_attrs({
        'long_name': "Scene classification",
        'definition': '0: aer (aerosols only) / 1: high_cloud (base cloud above 6096 m) / 2: mid_cloud (base cloud between 1981 m and 6096 m) / 3: low-cloud (base cloud below 1981 m) - 4: foc (fog or condensation)'
    })

    # add scene for extinction profile: cloud_above, cloud_below
    retrieval_scene = _classify_retrieval_scene(ds_towrite)
    # add scene as new dataarray
    ds_towrite["retrieval_scene"] = ("time", retrieval_scene)
    ds_towrite["retrieval_scene"] = ds_towrite["retrieval_scene"].assign_attrs({
        'long_name': "Retrieval scene classification",
        'definition': '0: aer (aerosols only) / 1: cloud_above (cloud above reference altitude) / 3: cloud_below (cloud below reference point) / 4: foc (fog or condensation)'
    })

    # drop other variables
    drop_variables = ['start_time', 'cloud_base_height', 'vertical_visibility', 'cbh_uncertainties', 'uncertainties_att_backscatter_0']
    for drop_var in drop_variables:
        ds_towrite = ds_towrite.drop(drop_var)
    
    # some variables have no dimension. Set it as attribute and drop the variable.
    nodim_variables = ['l0_wavelength', 'station_latitude', 'station_longitude', 'station_altitude']
    for nodim_var in nodim_variables:
        ds_towrite.attrs[nodim_var] = ds_towrite[nodim_var].data
        ds_towrite = ds_towrite.drop(nodim_var)

    # converts time
    ds_towrite = _convert_time_after_epoch(ds_towrite, resolution='ms')

    # writes to netcdf
    ds_towrite.to_netcdf(path, mode='w')

