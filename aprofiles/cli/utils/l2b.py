#!/usr/bin/env python

import os
import sys
from pathlib import Path

from glob import glob

import xarray as xr
import pandas as pd
from rich.progress import track

def make_files(path_in: Path, path_out: Path, progress_bar: bool) -> None:
    
    # list all AP files in path_in
    files = glob(f"{path_in}/AP*nc")

    for f in track(files, description=f"Reading AP files", disable=not progress_bar):

        ds = xr.open_dataset(f, decode_times=True, chunks=-1).load()
        # get unique id and extract yyyymmdd from first time step
        unique_id = f"{ds.attrs['wigos_station_id']}_{ds.attrs['instrument_id']}"
        yyyymmdd = str(ds.time.data[0].astype('M8[D]')).replace('-','')        
        
        ntimes = ds.time.size
        if ntimes < 60:
            myrange = range(ntimes)
        else:
            myrange = range(ntimes-12, ntimes)

        for i in myrange:
            ds1t = ds.isel(time=i)
            mmhh = pd.to_datetime(ds1t.time.data).strftime('%H%M')
            file_name = Path(path_out, f"{unique_id}_{yyyymmdd}{mmhh}.nc")
            ds1t.to_netcdf('out.nc')
            os.rename('out.nc',file_name)


