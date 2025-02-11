    # @author Augustin Mortier
# @desc A-Profiles - Code for creating climatology json file to be used in V-Profiles

from datetime import datetime
from pathlib import Path
import os

import numpy as np
import orjson
import xarray as xr


def compute_climatology(path, station_id, season_variables, all_variables, aerosols_only):
    # get all files
    station_files = []
    for root, dirs, files in os.walk(path, followlinks=True):
        for file in files:
            if station_id in file and file.endswith(".nc"):
                station_files.append(os.path.join(root, file))
    
    try:
        # open dataset with xarray
        vars = season_variables + all_variables + ['retrieval_scene', 'cloud_amount', 'scene']
        ds = xr.open_mfdataset(station_files, parallel=False, decode_times=True, chunks=-1, combine='nested', compat='override')[vars].load()
        
        # store attributes which are destroyed by the resampling method
        attrs = ds.attrs
        # replace np.int by int
        for attr in attrs:
            if isinstance(attrs[attr], np.uint32):
                attrs[attr] = int(attrs[attr])
        
        # keep only clear scenes
        if aerosols_only:
            ds = ds.where((ds.retrieval_scene <= 1) & (ds.cloud_amount == 0))
            
        # seasonal resampling
        Qds = ds.resample(time="QE").mean().compute()

        # add some statistics
        attrs["ndays"] = {"ndays": len(station_files), "since": str(ds.time.data[0]).split("T")[0]}
        attrs["today"] = datetime.today().strftime("%Y-%m-%d")

        # add number of days per season as a new variable
        Qds["ndays"] = ds.scene.resample(time="D").count().resample(time="QE").count()

        # add Z to time
        ds.coords['time'] = (ds['time'].astype(int)  * 1e-6).astype(int)
        Qds.coords['time'] = (Qds['time'].astype(int)  * 1e-6).astype(int)

        # round altitude to 3 decimals
        ds.coords['altitude'] = ds['altitude'].round(3)
        Qds.coords['altitude'] = Qds['altitude'].round(3)

        # select variables
        multivars_dict = {}

        # add seasonal variables
        for var in season_variables + ["ndays"]:
            multivars_dict[var] = Qds[var].round(6).to_dict()
        
        # add all variables
        for var in all_variables:
            multivars_dict[var] = ds[var].round(6).to_dict()

        # add attributes as separate key
        multivars_dict["attrs"] = attrs

        # define path
        clim_path = Path(path, "climato")
        # create directory if does not exist
        clim_path.mkdir(parents=True, exist_ok=True)

        # write data to json file
        with open(Path(clim_path, f"AP_{station_id}_clim.json"), 'wb') as json_file:
            json_file.write(orjson.dumps(multivars_dict, option=orjson.OPT_SERIALIZE_NUMPY))

    except ValueError:
        print(f'ValueError encountered with {station_id}')
