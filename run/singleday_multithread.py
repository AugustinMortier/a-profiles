#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles - Run aprofiles workflow for all stations in series for a given day

import concurrent.futures
import os

from tqdm import tqdm

import run

BASE_DIR_IN = 'data/e-profile'
BASE_DIR_OUT = 'data/v-profiles'

def _main():

    instrument_types = ['CHM15k', 'miniMPL']

    date = '2021-09-10'

    yyyy = date.split('-')[0]
    mm = date.split('-')[1]
    dd = date.split('-')[2]

    # list all files in in directory
    datepath = os.path.join(BASE_DIR_IN, yyyy, mm, dd)
    onlyfiles = [f for f in os.listdir(datepath) if os.path.isfile(os.path.join(datepath, f))]
    
    # data processing
    with tqdm(total=len(onlyfiles)) as pbar:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(run.workflow.workflow, path=os.path.join(datepath, filename), instrument_types=instrument_types, base_dir=BASE_DIR_OUT, verbose=False) for filename in onlyfiles]
            for future in concurrent.futures.as_completed(futures):
                pbar.update(1)

    # list all files in out directory
    datepath = os.path.join(BASE_DIR_OUT, yyyy, mm, dd)
    onlyfiles = [f for f in os.listdir(datepath) if os.path.isfile(os.path.join(datepath, f))]
    
    # create calendar
    calname = f"{yyyy}-{mm}-cal.json"
    if not os.path.exists(os.path.join(BASE_DIR_OUT, yyyy, mm, 'calendar', calname)):
        run.json_calendar.make_calendar(BASE_DIR_OUT, yyyy, mm, calname)

    # add to calendar
    for i in (tqdm(range(len(onlyfiles)), desc='calendar  ')):
        fn = os.path.join(BASE_DIR_OUT, yyyy, mm, dd, onlyfiles[i])
        run.json_calendar.add_to_calendar(fn, BASE_DIR_OUT, yyyy, mm, dd, calname)

    # create map
    mapname = f"{yyyy}-{mm}-map.json"
    if not os.path.exists(os.path.join(BASE_DIR_OUT, yyyy, mm, mapname)):
        run.json_map.make_map(BASE_DIR_OUT, yyyy, mm, mapname)

    # add to map
    for i in (tqdm(range(len(onlyfiles)), desc='map       ')):
        fn = os.path.join(BASE_DIR_OUT, yyyy, mm, dd, onlyfiles[i])
        run.json_map.add_to_map(fn, BASE_DIR_OUT, yyyy, mm, dd, mapname)
    
if __name__ == "__main__":
    _main()
