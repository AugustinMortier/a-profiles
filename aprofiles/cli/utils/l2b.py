#!/usr/bin/env python
import os
import sys
from pathlib import Path

from glob import glob

import xarray as xr
import pandas as pd
from rich.progress import track

def make_files(path_in: Path, path_out: Path, time_steps: int, progress_bar: bool) -> None:
    
    # list all AP files in path_in
    files = list(Path(path_in).glob("AP*nc"))

    for f in track(files, description=f"Reading AP files", disable=not progress_bar):

        ds = xr.open_dataset(f, decode_times=True, chunks=-1)
        # get unique id and extract yyyymmdd from first time step
        unique_id = f"{ds.attrs['wigos_station_id']}_{ds.attrs['instrument_id']}"
        yyyymmdd = str(ds.time.data[0].astype('M8[D]')).replace('-','')        
        
        # we just work with the 6 latest time steps, that is 30 min worth of data
        start_idx = max(0, ds.time.size - time_steps)
        ds30min = ds.isel(time=slice(start_idx,ds.time.size))
        mmhh = pd.to_datetime(ds30min.time[0].data).strftime('%H%M')
        
        # write output file
        file_name = Path(path_out, f"L2B_{unique_id}{yyyymmdd}{mmhh}.nc")
        ds30min.to_netcdf('out.tmp')
        os.rename('out.tmp',file_name)
