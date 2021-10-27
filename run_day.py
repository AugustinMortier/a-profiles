#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles - Run aprofiles worflow for all stations for a given day

from os import listdir
from os.path import isfile, join
import time

import aprofiles as apro

start_time = time.time()

BASE_DIR = 'data/e-profiles'
date = '2021-09-09'

# list all files in directory
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

# read some data
path = "examples/data/E-PROFILE/L2_0-20000-006735_A20210908.nc"
path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"

apro_reader = apro.reader.ReadProfiles(path)
profiles = apro_reader.read()

def aprofiles_worflow(path):
    apro_reader = apro.reader.ReadProfiles(path)
    profiles = apro_reader.read()

    # extrapolation lowest layers
    profiles.extrapolate_below(z=150, inplace=True)

    # detection
    profiles.foc(zmin_cloud=200)
    profiles.clouds(zmin=300, thr_noise=5, thr_clouds=4, verbose=True)
    profiles.pbl(zmin=200, zmax=3000, under_clouds=False, min_snr=2.0, verbose=True)

    # retrievals
    profiles.inversion(zmin=4000., zmax=6000., remove_outliers=True, method="forward", verbose=True)
    profiles.write(dataset=profiles.data, basedir='~/dev/v-profiles/data_web_api')

print("--- %s seconds ---" % (time.time() - start_time))
