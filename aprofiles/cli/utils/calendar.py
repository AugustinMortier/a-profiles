# @author Augustin Mortier
# @desc A-Profiles - Code for creating calendar json file to be used in V-Profiles

import json
from pathlib import Path

import xarray as xr


def make_calendar(path, yyyy: str, mm: str, calname: str) -> None:
    # one calendar, per month
    with open(Path(path, yyyy, mm, calname), 'w') as json_file:
        json.dump({}, json_file)

def add_to_calendar(fn, path, yyyy: str, mm: str, dd: str, calname: str) -> None:
    # calendar collects the number of inversions with no low-level clouds (<6km) at each station
    # for each station, write number of each scene class (aer, cloud<6km, cloud>6km, )
    
    # read data
    vars_to_read = ['retrieval_scene']
    
    # in some cases, the file might be corrupted. Just skip it then.
    try:
        ds = xr.open_dataset(fn, engine='netcdf4', chunks=-1)[vars_to_read].load()
    except OSError:
        print(f'File {fn} is corrupted. Skipping...')
        return

    # counts scenes
    scene_classes = [4, 3, 1, 0]
    scene_counts = {}
    for scene_class in scene_classes:
        scene_counts[scene_class] = len(ds.retrieval_scene.data[ds.retrieval_scene.data == scene_class])
    scene_counts['total'] = len(ds.retrieval_scene.data)

    # open current calendar
    with open(Path(path, yyyy, mm, calname), 'r') as json_file:
        data = json.load(json_file)
    json_file.close()        

    # add new data to calendar data
    station_id = f'{ds.attrs["wigos_station_id"]}-{ds.attrs["instrument_id"]}'
    if station_id not in data:
        data[station_id] = {}
    data[station_id][dd] = scene_counts

    # write new calendar
    with open(Path(path, yyyy, mm, calname), 'w') as json_file:
        json.dump(data, json_file)
