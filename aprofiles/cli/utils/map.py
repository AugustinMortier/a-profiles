# @author Augustin Mortier
# @desc A-Profiles - Code for creating map json file to be used in V-Profiles

import json
import warnings
from pathlib import Path

import numpy as np
import xarray as xr


def make_map(path, yyyy: str, mm: str, mapname) -> None:
    # one map, per day, which collects the maximum extinction with no low-level clouds (<6km) at each station
    with open(Path(path, yyyy, mm, mapname), "w") as json_file:
        json.dump({}, json_file)


def add_to_map(fn, path, yyyy: str, mm: str, dd: str, mapname) -> None:
    # map collects the maximum extinction value with no low-level clouds (<6km) at each station at a hourly resolution
    # for each station, write an array with extinction values, and array with scenes for each hour of the day

    # read data
    vars_to_read = [
        "extinction",
        "retrieval_scene",
        "cloud_amount",
        "lidar_ratio",
        "aer_type",
        "mec",
    ]

    # in some cases, the file might be corrupted. Just skip it then.
    try:
        ds = xr.open_dataset(fn, engine="netcdf4", chunks=-1)[vars_to_read].load()
    except OSError:
        print(f"File {fn} is corrupted. Skipping...")
        return

    # calculate the max extinction and determine the scene for each hour of the day
    # need to convert time (from int to datetime) in order to use the resample method from xarray
    ds["time"] = ds.time.data.astype("datetime64[ms]").astype("datetime64[ns]")

    # in order to prevent some monotony issue, sort by time
    ds = ds.sortby("time")

    layers = ["0-6", "0-2", "2-4", "4-6"]
    max_ext = {}
    for layer in layers:
        zmin = float(layer.split("-")[0]) * 1000
        zmax = float(layer.split("-")[1]) * 1000
        zmin_asl = zmin + ds.attrs["station_altitude_t0"]
        zmax_asl = zmax + ds.attrs["station_altitude_t0"]

        # extinction for each hour
        max_ext_profiles = (
            ds.where((ds.altitude >= zmin_asl) & (ds.altitude < zmax_asl), drop=True)
            .extinction.resample(time="1h")
            .max()
            .data
        )

        # take the maximum value in each profile
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            max_ext[layer] = np.nanmax(max_ext_profiles, axis=1)

    # scene for each hour
    max_retrieval_scene = ds.retrieval_scene.resample(time="1h").max().data
    max_cloud_amount = ds.cloud_amount.resample(time="1h").max().data
    mean_lidar_ratio = ds.lidar_ratio.resample(time="1h").mean().data

    # make mec dictionary
    mec = dict()
    for i, aer_type in enumerate(ds.aer_type.data):
        mec[aer_type] = round(float(ds.mec[i].data), 3)

    # open current map
    with open(Path(path, yyyy, mm, mapname), "r") as json_file:
        data = json.load(json_file)
    json_file.close()

    # add new data to calendar data
    station_id = f'{ds.attrs["wigos_station_id"]}-{ds.attrs["instrument_id"]}'
    if station_id not in data:
        data[station_id] = {}
    data[station_id][dd] = {
        "attrs": {
            "coords": {
                "latitude": ds.attrs["station_latitude_t0"],
                "longitude": ds.attrs["station_longitude_t0"],
                "altitude": ds.attrs["station_altitude_t0"],
            },
            "l0_wavelength": ds.attrs["l0_wavelength"],
            "station_id": station_id,
            "station_name": ds.attrs["site_location"],
            "instrument_type": ds.attrs["instrument_type"],
        },
        "max_ext:0-6km": [
            round(ext, 4) if not np.isnan(ext) else None for ext in max_ext["0-6"]
        ],
        "max_ext:0-2km": [
            round(ext, 4) if not np.isnan(ext) else None for ext in max_ext["0-2"]
        ],
        "max_ext:2-4km": [
            round(ext, 4) if not np.isnan(ext) else None for ext in max_ext["2-4"]
        ],
        "max_ext:4-6km": [
            round(ext, 4) if not np.isnan(ext) else None for ext in max_ext["4-6"]
        ],
        "retrieval_scene": [
            retrieval_scene if not np.isnan(retrieval_scene) else None
            for retrieval_scene in max_retrieval_scene.tolist()
        ],
        "cloud_amount": [
            cloud_amount if not np.isnan(cloud_amount) else None
            for cloud_amount in max_cloud_amount.tolist()
        ],
        "lidar_ratio": [
            lidar_ratio if not np.isnan(lidar_ratio) else None
            for lidar_ratio in mean_lidar_ratio.tolist()
        ],
        "mec": mec,
    }

    # write new map
    with open(Path(path, yyyy, mm, mapname), "w") as json_file:
        json.dump(data, json_file)
