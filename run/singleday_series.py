# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles - Run aprofiles workflow for all stations in series for a given day

import os

from tqdm import tqdm

import run

BASE_DIR_IN = 'data/e-profile'
BASE_DIR_OUT = 'data/v-profiles'

def _main(date: str, instrument_types=['CHM15k', 'mini-MPL']):

    yyyy = date.split('-')[0]
    mm = date.split('-')[1]
    dd = date.split('-')[2]

    # list all files in in directory
    datepath = os.path.join(BASE_DIR_IN, yyyy, mm, dd)
    onlyfiles = [f for f in os.listdir(datepath) if os.path.isfile(os.path.join(datepath, f))]
    
    # data processing
    for i in (tqdm(range(len(onlyfiles)), desc=date)):
        path = os.path.join(datepath, onlyfiles[i])
        run.workflow.workflow(path, instrument_types, BASE_DIR_OUT, verbose=False)
    
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
    import sys
    if len(sys.argv)>1:
        _main(sys.argv[1])
    else:
        _main('2021-09-09')
