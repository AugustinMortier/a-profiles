#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles - Code for creating map json file to be used in V-Profiles

import json
import os

import numpy as np
import xarray as xr


def make_map(base_dir, yyyy, mm, dd, mapname):
    # one map, per day, which collects the maximum extinction with no low-level clouds (<6km) at each station
    with open(os.path.join(base_dir, yyyy, mm, dd, mapname), 'w') as json_file:
        json.dump({}, json_file)

def add_to_map(fn, base_dir, yyyy, mm, dd, mapname):
    # map collects the maximum extinction value with no low-level clouds (<6km) at each station at a hourly resolution
    # for each station, write an array with extinction values, and array with scenes for each hour of the day
    
    # read data
    ds = xr.open_dataset(fn)

    # calculate the max extinction and determine the scene for each hour of the day
    # need to convert time (from int to datetime) in order to use the resample method from xarray
    ds = ds.assign_coords(time = ds.time.data.astype("datetime64[ms]"))

    # extinction for each hour
    max_ext_profiles = ds.extinction.resample(time="1H").max().data

    # take the maximum value in each profile
    max_ext = np.nanmax(max_ext_profiles, axis=1)

    # scene for each hour
    # attribute a weight to each scene in order to prioritize the scenes
    scene_weights = {'foc': 4, 'low_cloud': 3, 'mid_cloud': 2, 'high_cloud': 1, 'aer': 0}
    scene = np.asarray(ds.scene.data)
    for scene_weight in scene_weights.keys():
        scene[scene==scene_weight] = scene_weights[scene_weight]

    # creates dataarrays in order to resample with xarray method
    ds["weight_scene"] = ('time', scene)
    # takes the highest weight for resampled data
    max_weight = ds.scene.resample(time="1H").max().data

    # reverse dictionnary
    weight_scenes = {v: k for k, v in scene_weights.items()}
    max_scene = max_weight
    for weight_scene in weight_scenes.keys():
        max_scene[max_scene==weight_scene] = weight_scenes[weight_scene]

    # open current map
    mapname = 'map.json'
    with open(os.path.join(base_dir, yyyy, mm, dd, mapname), 'r') as json_file:
        data = json.load(json_file)
    json_file.close()        

    # add new data to calendar data
    station_id = ds.attrs['wigos_station_id']
    if station_id not in data:
        data[station_id] = {}
    data[station_id][dd] = {
        'ext': max_ext.tolist(),
        'scene': max_scene.tolist()
    }

    # write new map
    with open(os.path.join(base_dir, yyyy, mm, dd, mapname), 'w') as json_file:
        json.dump(data, json_file)
