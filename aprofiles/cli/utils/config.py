# @author Augustin Mortier
# @desc A-Profiles - Read config file

import json
import os.path

def read():
    # read alc_parameters files
    CFG_FILE_PATH = os.path.join(os.path.dirname(__file__),'..', 'config', 'cfg.json') 
    with open(CFG_FILE_PATH) as json_file:
        return json.load(json_file)

