# @author Augustin Mortier
# @desc A-Profiles - Read config file

import json
from pathlib import Path


def read():
    # read alc_parameters files
    with open(Path(Path(__file__).parent, '..', 'config', 'cfg.json')) as json_file:
        return json.load(json_file)
