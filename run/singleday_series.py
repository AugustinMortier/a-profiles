#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles - Run aprofiles workflow for all stations in series for a given day

import json
import os
import time

import numpy as np
from tqdm import tqdm
import xarray as xr

import run


BASE_DIR_IN = 'data/e-profile'
BASE_DIR_OUT = 'data/v-profiles'

def _main():

    instrument_types = ['CHM15k', 'miniMPL']

    date = '2021-09-09'

    yyyy = date.split('-')[0]
    mm = date.split('-')[1]
    dd = date.split('-')[2]

    """
    # list all files in in directory
    datepath = os.path.join(BASE_DIR_IN, yyyy, mm, dd)
    onlyfiles = [f for f in os.listdir(datepath) if os.path.isfile(os.path.join(datepath, f))]

    # data processing
    for i in (tqdm(range(len(onlyfiles)), desc=date)):
        path = os.path.join(datepath, onlyfiles[i])
        run.workflow.workflow(path, instrument_types, BASE_DIR_IN, verbose=False)
    """
    
    # list all files in out directory
    datepath = os.path.join(BASE_DIR_OUT, yyyy, mm, dd, 'profiles')
    onlyfiles = [f for f in os.listdir(datepath) if os.path.isfile(os.path.join(datepath, f))]
    
    # create calendar
    calname = '{}-{}-cal.json'.format(yyyy, mm)
    if not os.path.exists(os.path.join(BASE_DIR_OUT, yyyy, mm, 'calendar', calname)):
        run.json_calendar.make_calendar(BASE_DIR_OUT, yyyy, mm, calname)

    # add to calendar
    for i in (tqdm(range(len(onlyfiles)), desc='calendar')):
        fn = os.path.join(BASE_DIR_OUT, yyyy, mm, dd, 'profiles', onlyfiles[i])
        run.json_calendar.add_to_calendar(fn, BASE_DIR_OUT, yyyy, mm, dd, calname)

    # create map
    mapname = '{}-{}-{}-map.json'.format(yyyy, mm, dd)
    if not os.path.exists(os.path.join(BASE_DIR_OUT, yyyy, mm, dd, mapname)):
        run.json_map.make_map(BASE_DIR_OUT, yyyy, mm, dd, mapname)

    # add to map
    for i in (tqdm(range(len(onlyfiles)), desc='map     ')):
        fn = os.path.join(BASE_DIR_OUT, yyyy, mm, dd, 'profiles', onlyfiles[i])
        run.json_map.add_to_map(fn, BASE_DIR_OUT, yyyy, mm, dd, mapname)
    
if __name__ == "__main__":
    _main()
