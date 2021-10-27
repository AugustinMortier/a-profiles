#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles - Run aprofiles workflow for all stations in a pool of workers for a given day

import os
import time

import aprofiles as apro
from multiprocessing import Pool, TimeoutError
from tqdm import tqdm

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
        profiles.write(base_dir='~/dev/v-profiles/data_web_api')

def make_calendar():
    # one calendar, per month, which collects the number of inversions with no low-level clouds (<6km) at each station
    pass

def make_map():
    # one map, per day, which collects the maximum extinction with no low-level clouds (<6km) at each station
    pass

def _main():
    
    BASE_DIR = 'data/e-profile'
    instrument_types = ['CHM15k', 'miniMPL']

    date = '2021-09-09'

    # list all files in directory
    yyyy = date.split('-')[0]
    mm = date.split('-')[1]
    dd = date.split('-')[2]
    datepath = os.path.join(BASE_DIR, yyyy, mm, dd)
    onlyfiles = [f for f in os.listdir(datepath) if os.path.isfile(os.path.join(datepath, f))]

    def _pool_workflow(i):
        path = os.path.join(datepath, onlyfiles[i])
        aprofiles_workflow(path, instrument_types, verbose=False)

    # data processing
    pool = Pool(processes=4)
    zip(*pool.map(_pool_workflow, range(0, len(onlyfiles))))

    # create calendar

    # create map

if __name__ == "__main__":
    _main()
