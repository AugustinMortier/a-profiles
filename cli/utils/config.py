# @author Augustin Mortier
# @desc A-Profiles - Read config file

import json


def read():
    # read alc_parameters files
    with open('cli/config/cfg.json') as json_file:
        return json.load(json_file)
