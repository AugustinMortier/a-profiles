# @author Augustin Mortier
# @desc A-Profiles - Code for creating climatology json file to be used in V-Profiles

from datetime import date, datetime, time
import json
from pathlib import Path
import os

import numpy as np
import orjson
import pandas as pd
import xarray as xr


def compute_climatology(basedir, station_id, variables, aerosols_only):
    # get all files
    station_files = []
    for root, dirs, files in os.walk(basedir, followlinks=True):
        for file in files:
            if station_id in file and file.endswith(".nc"):
                station_files.append(os.path.join(root, file))

    try:
        # open dataset with xarray
        ds = xr.open_mfdataset(station_files, parallel=False, decode_times=True)

        # store attributes which are destroyed by the resampling method
        attrs = ds.attrs
        # replace np.int by int
        for attr in attrs:
            if isinstance(attrs[attr], np.uint32):
                attrs[attr] = int(attrs[attr])

        # keep only clear scenes
        if aerosols_only:
            ds = ds.where((ds.retrieval_scene <= 1) & (ds.cloud_amount == 0))

        # add some statistics
        attrs["ndays"] = {"ndays": len(station_files), "since": str(ds.time.data[0]).split("T")[0]}
        attrs["today"] = datetime.today().strftime("%Y-%m-%d")

        # seasonal resampling
        Qds = ds.resample(time="QE").mean()
        # add number of days per season as a new variable
        Qds["ndays"] = ds.scene.resample(time="D").count().resample(time="QE").count()

        # work with selected variable

        # select variables
        multivars_dict = {}
        vars = variables.split("-")
        vars.append("ndays")

        for var in vars:
            # dataarray
            da = Qds[var]
            multivars_dict[var] = da.to_dict()

        # add attributes as separate key
        multivars_dict["attrs"] = attrs

        # define path
        clim_path = Path(basedir, "climato")
        # create directory if does not exist
        clim_path.mkdir(parents=True, exist_ok=True)

        # write data to json file
        with open(Path(clim_path, f"AP_{station_id}_clim.json"), 'wb') as json_file:
            json_file.write(orjson.dumps(multivars_dict, option=orjson.OPT_SERIALIZE_NUMPY))

    except ValueError:
        print(f'ValueError encountered with {station_id}')
