# @author Augustin Mortier
# @desc A-Profiles - Code for creating map json file to be used in V-Profiles

import json
import warnings
from pathlib import Path

import numpy as np
import xarray as xr


def make_map(base_dir, yyyy, mm, mapname):
    # one map, per day, which collects the maximum extinction with no low-level clouds (<6km) at each station
    with open(Path(base_dir) / yyyy / mm / mapname, 'w') as json_file:
        json.dump({}, json_file)

def add_to_map(fn, base_dir, yyyy, mm, dd, mapname):
    # map collects the maximum extinction value with no low-level clouds (<6km) at each station at a hourly resolution
    # for each station, write an array with extinction values, and array with scenes for each hour of the day
    
    # read data
    ds = xr.open_dataset(fn)

    # calculate the max extinction and determine the scene for each hour of the day
    # need to convert time (from int to datetime) in order to use the resample method from xarray
    ds["time"]= ds.time.data.astype("datetime64[ms]").astype("datetime64[ns]")

    # in order to prevent some monotony issue, sort by time
    ds = ds.sortby('time')

    layers = ['0-6', '0-2', '2-4', '4-6']
    max_ext = {}
    for layer in layers:
        zmin = float(layer.split('-')[0])*1000
        zmax = float(layer.split('-')[1])*1000
        zmin_asl = zmin + ds.attrs['station_altitude']
        zmax_asl = zmax + ds.attrs['station_altitude']
        
        # extinction for each hour
        max_ext_profiles = ds.where((ds.altitude>=zmin_asl) & (ds.altitude<zmax_asl), drop=True).extinction.resample(time="1h").max().data

        # take the maximum value in each profile
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            max_ext[layer] = np.nanmax(max_ext_profiles, axis=1)

    # scene for each hour
    max_retrieval_scene = ds.retrieval_scene.resample(time='1h').max().data
    max_cloud_amount = ds.cloud_amount.resample(time='1h').max().data

    # open current map
    with open(Path(base_dir) / yyyy / mm / mapname, 'r') as json_file:
        data = json.load(json_file)
    json_file.close()        

    # add new data to calendar data
    station_id = f'{ds.attrs["wigos_station_id"]}-{ds.attrs["instrument_id"]}'
    if station_id not in data:
        data[station_id] = {}
    data[station_id][dd] = {
        'attrs': {
            'coords': {
                'latitude': ds.attrs['station_latitude'],
                'longitude': ds.attrs['station_longitude'],
                'altitude': ds.attrs['station_altitude'],
            },
            'l0_wavelength': ds.attrs['l0_wavelength'],
            'station_id': station_id,
            'station_name': ds.attrs['site_location'],
            'instrument_type': ds.attrs['instrument_type']
        },
        'max_ext:0-6km': [round(ext,4) if not np.isnan(ext) else None for ext in max_ext['0-6']],
        'max_ext:0-2km': [round(ext,4) if not np.isnan(ext) else None for ext in max_ext['0-2']],
        'max_ext:2-4km': [round(ext,4) if not np.isnan(ext) else None for ext in max_ext['2-4']],
        'max_ext:4-6km': [round(ext,4) if not np.isnan(ext) else None for ext in max_ext['4-6']],
        'retrieval_scene': [retrieval_scene if not np.isnan(retrieval_scene) else None for retrieval_scene in max_retrieval_scene.tolist()],
        'cloud_amount': [cloud_amount if not np.isnan(cloud_amount) else None for cloud_amount in max_cloud_amount.tolist()],
    }

    # write new map
    with open(Path(base_dir) / yyyy / mm / mapname, 'w') as json_file:
        json.dump(data, json_file)
