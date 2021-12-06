# @author Augustin Mortier
# @desc A-Profiles - AERONET reading class

import xarray as xr


class ReadAERONET:
    """AERONET reading class.

    Data:
        [https://data.ceda.ac.uk/badc/eprofile/data/daily_files/]

    Attributes:
        path (str): The path of the file to be read (path or URL).
    """

    def __init__(self, path):
        self.path = path
