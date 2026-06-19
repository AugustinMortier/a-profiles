# @author Augustin Mortier
# @desc A-Profiles - Code for creating climatology json file to be used in V-Profiles

from datetime import datetime
from pathlib import Path
import os
from turtle import pd

import numpy as np
import orjson
import xarray as xr


def compute_climatology(
    path_in, path_out, station_id, season_variables, all_variables, aerosols_only, n_days
):
    # define path
    clim_daily_path = Path(path_out, "climato_daily")
    # create directory if does not exist
    clim_daily_path.mkdir(parents=True, exist_ok=True)
    clim_daily_file = Path(clim_daily_path, f"AP_{station_id}_clim.nc")
    
    # define path
    clim_path = Path(path_out, "climato")
    # create directory if does not exist
    clim_path.mkdir(parents=True, exist_ok=True)
    clim_json_file = Path(clim_path, f"AP_{station_id}_clim.json")
    
    # get all files
    station_files = []
    for root, dirs, files in os.walk(path_in, followlinks=True):
        for file in files:
            if station_id in file and file.endswith(".nc"):
                file_date = file.split("_")[2]
                if file_date >= (datetime.today() - pd.Timedelta(days=n_days)).strftime("%Y%m%d"):
                    station_files.append(os.path.join(root, file))
    print(f"Looking for files in {path_in} for station {station_id} in the last {n_days} days...")
    print(f"Found {len(station_files)} files for station {station_id} in the last {n_days} days.")
    
    # open existing climatology files if they exist so that we can update them with new data
    if clim_daily_file.exists():
        existing_ds = xr.open_dataset(clim_daily_file)

    station_files = sorted(station_files)
    try:
        # open dataset with xarray
        vars = (
            season_variables
            + all_variables
            + ["retrieval_scene", "cloud_amount", "scene"]
        )
        try:
            ds = xr.open_mfdataset(
                station_files,
                parallel=False,
                decode_times=True,
                chunks=-1,
                concat_dim="time",
                join="outer",
                data_vars=vars,
                coords="minimal",
                combine="nested",
                compat="override",
                drop_variables=["mec"],
            )[vars].load()
        except Exception as e:
            raise (e)

        ds = ds.sortby("time")
        ds = ds.drop_duplicates("time", keep="last")

        # store attributes which are destroyed by the resampling method
        attrs = ds.attrs
        # replace np.int by int
        for attr in attrs:
            if isinstance(attrs[attr], np.uint32):
                attrs[attr] = int(attrs[attr])

        # keep only clear scenes
        if aerosols_only:
            ds = ds.where((ds.retrieval_scene <= 1) & (ds.cloud_amount == 0))
        
        # add data to existing climatology if it exists
        if clim_daily_file.exists():
            ds = xr.concat([existing_ds, ds], dim="time").sortby("time").drop_duplicates("time", keep="last")

        # daily resampling
        Dds = ds.resample(time="D").mean().compute()
        Dds["nprofiles"] = ds.scene.resample(time="D").count().compute()

        # write daily file
        Dds.to_netcdf(clim_daily_file)

        # seasonal resampling
        Qds = ds.resample(time="QE").mean().compute()

        # add some statistics
        attrs["ndays"] = {
            "ndays": len(station_files),
            "since": str(ds.time.data[0]).split("T")[0],
        }
        attrs["today"] = datetime.today().strftime("%Y-%m-%d")

        # add number of days per season as a new variable
        Qds["ndays"] = ds.scene.resample(time="D").count().resample(time="QE").count()

        # add Z to time
        ds.coords["time"] = (ds["time"].astype(int) * 1e-6).astype(int)
        Qds.coords["time"] = (Qds["time"].astype(int) * 1e-6).astype(int)

        # round altitude to 3 decimals
        ds.coords["altitude"] = ds["altitude"].round(3)
        Qds.coords["altitude"] = Qds["altitude"].round(3)

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

        # write data to json file
        # if file exists, update it with new data
        if clim_json_file.exists():
            with open(clim_json_file, "rb") as json_file:
                existing_data = orjson.loads(json_file.read())
            existing_data.update(multivars_dict)
            with open(clim_json_file, "wb") as json_file:
                json_file.write(
                    orjson.dumps(existing_data, option=orjson.OPT_SERIALIZE_NUMPY)
                )

    except Exception as e:
        print(f"Error encountered with {station_id}: {e}")
