# @author Augustin Mortier
# @desc A-Profiles - Code for creating climatology json file to be used in V-Profiles

from datetime import datetime, timedelta
from pathlib import Path
import os
import numpy as np
import xarray as xr


def compute_climatology(
    path_in,
    path_out,
    station_id,
    season_variables,
    all_variables,
    aerosols_only,
    n_days,
):
    # ------------------------------------------------------------------
    # paths
    # ------------------------------------------------------------------
    clim_path = Path(path_out, "climato")
    clim_path.mkdir(parents=True, exist_ok=True)

    clim_file = clim_path / f"AP_{station_id}_clim.nc"

    # ------------------------------------------------------------------
    # discover recent files
    # ------------------------------------------------------------------
    cutoff_dt = datetime.today() - timedelta(days=n_days)
    cutoff = cutoff_dt.strftime("%Y%m%d")

    station_files = []

    for root, _, files in os.walk(path_in, followlinks=True):
        for file in files:
            if station_id not in file or not file.endswith(".nc"):
                continue

            try:
                file_yyyymmdd = file.split(f"AP_{station_id}-")[1].split(".nc")[0]
                file_date = datetime.strptime(file_yyyymmdd, "%Y-%m-%d").strftime("%Y%m%d")
            except Exception:
                continue

            if file_date >= cutoff:
                station_files.append(os.path.join(root, file))

    station_files = sorted(station_files)

    if not station_files:
        return

    try:
        vars = (
            season_variables
            + all_variables
            + ["retrieval_scene", "cloud_amount", "scene"]
        )

        # ------------------------------------------------------------------
        # load raw profiles
        # ------------------------------------------------------------------
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

        ds = ds.sortby("time").drop_duplicates("time", keep="last")

        # ------------------------------------------------------------------
        # aerosol filtering
        # ------------------------------------------------------------------
        if aerosols_only:
            mask = (ds.retrieval_scene <= 1) & (ds.cloud_amount == 0)
            ds = ds.where(mask, drop=False)

        # ------------------------------------------------------------------
        # build NEW daily climatology (from raw data only)
        # ------------------------------------------------------------------
        new_daily = ds.resample(time="D").mean(skipna=True)

        n_profiles = ds.scene.resample(time="D").count().fillna(0).astype(np.int32)
        n_profiles.attrs = {
            "long_name": "Number of profiles",
            "description": "Number of profiles used to compute the daily mean",
        }

        new_daily["n_profiles"] = n_profiles
        new_daily = new_daily.compute()

        # ------------------------------------------------------------------
        # merge with existing climatology (if any)
        # ------------------------------------------------------------------
        if clim_file.exists():
            with xr.open_dataset(clim_file) as old_daily:
                old_daily = old_daily.load()

            Dds = xr.concat([old_daily, new_daily], dim="time")
            Dds = Dds.sortby("time").drop_duplicates("time", keep="last")
        else:
            Dds = new_daily

        # ------------------------------------------------------------------
        # metadata
        # ------------------------------------------------------------------
        Dds.attrs["n_days"] = np.int32(Dds.sizes["time"])
        Dds.attrs["since"] = str(Dds.time.values[0]).split("T")[0]
        Dds.attrs["today"] = datetime.today().strftime("%Y-%m-%d")

        # ------------------------------------------------------------------
        # write output
        # ------------------------------------------------------------------
        Dds.to_netcdf(clim_file)
        # close datasets
        ds.close()
        Dds.close()

    except Exception as e:
        print(f"Error encountered with {station_id}: {e}")