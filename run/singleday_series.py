#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles - Run aprofiles workflow for all stations in series for a given day

import json
import os
import time

import aprofiles as apro
import numpy as np
from tqdm import tqdm
import xarray as xr

BASE_DIR_IN = 'data/e-profile'
BASE_DIR_OUT = 'data/v-profiles'

def aprofiles_workflow(path, instrument_types, verbose=False):
    apro_reader = apro.reader.ReadProfiles(path)
    profiles = apro_reader.read()

    # do the rest if instrument_type in the list
    if profiles.data.attrs['instrument_type'] in instrument_types:    

        # extrapolation lowest layers
        profiles.extrapolate_below(z=150., inplace=True)

        # detection
        profiles.foc(zmin_cloud=200.)
        profiles.clouds(zmin=300., thr_noise=5., thr_clouds=4., verbose=verbose)
        profiles.pbl(zmin=200., zmax=3000., under_clouds=False, min_snr=2., verbose=verbose)

        # retrievals
        profiles.inversion(zmin=4000., zmax=6000., remove_outliers=True, method="forward", verbose=verbose)
        profiles.write(base_dir=BASE_DIR_OUT)

def make_calendar(yyyy, mm, base_dir):
    # one calendar, per month
    calname = 'cal.json'
    with open(os.path.join(base_dir, yyyy, mm, calname), 'w') as json_file:
        json.dump({}, json_file)

def add_to_calendar(path, yyyy, mm, base_dir):
    # calendar collects the number of inversions with no low-level clouds (<6km) at each station
    # for each station, write number of each scene class (aer, cloud<6km, cloud>6km, )
    """
    # read data
    ds = xr.open_dataset(os.path.join(path, filename), decode_times=True)

    # open current calendar
    with open(os.path.join(base_dir, yyyy, mm, calname), 'w') as json_file:
        data = json.load(json_file)
    json_file.close()        

    # write new calendar
    calname = 'cal.json'
    with open(os.path.join(base_dir, yyyy, mm, calname), 'w') as json_file:
        json.dump(data, json_file)
    """
    pass

def make_map(yyyy, mm, dd, base_dir):
    # one map, per day, which collects the maximum extinction with no low-level clouds (<6km) at each station
    mapname = 'map.json'
    with open(os.path.join(base_dir, yyyy, mm, dd, mapname), 'w') as json_file:
        json.dump({}, json_file)

def _main():

    instrument_types = ['CHM15k', 'miniMPL']

    date = '2021-09-09'

    yyyy = date.split('-')[0]
    mm = date.split('-')[1]
    dd = date.split('-')[2]
    
    # list all files in in directory
    datepath = os.path.join(BASE_DIR_IN, yyyy, mm, dd)
    onlyfiles = [f for f in os.listdir(datepath) if os.path.isfile(os.path.join(datepath, f))]

    # data processing
    for i in (tqdm(range(len(onlyfiles)), desc=date)):
        path = os.path.join(datepath, onlyfiles[i])
        aprofiles_workflow(path, instrument_types, verbose=False)

    # list all files in out directory
    datepath = os.path.join(BASE_DIR_OUT, yyyy, mm, dd)
    onlyfiles = [f for f in os.listdir(datepath) if os.path.isfile(os.path.join(datepath, f))]
    
    # create calendar
    calname = 'cal.json'
    if not os.path.exists(os.path.join(BASE_DIR_OUT, yyyy, mm, calname)):
        make_calendar(yyyy, mm, base_dir=BASE_DIR_OUT)

    # add to calendar
    for i in (tqdm(range(len(onlyfiles)), desc='calendar')):
        path = os.path.join(BASE_DIR_OUT, yyyy, mm, dd, onlyfiles[i])
        add_to_calendar(path, yyyy, mm, base_dir=BASE_DIR_OUT)
    
    # create map
    mapname = 'map.json'
    if not os.path.exists(os.path.join(BASE_DIR_OUT, yyyy, mm, dd, mapname)):
        make_map(yyyy, mm, dd, base_dir=BASE_DIR_OUT)
    
if __name__ == "__main__":
    _main()
