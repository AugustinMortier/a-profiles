#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles - Reader class

import xarray as xr

from aprofiles.profiles_data import ProfilesData
from aprofiles.io import read_aeronet, read_eprofile

class ReadProfiles:
    """Base class for reading profiles data.

    Attributes:
        path (str): path of the file to be read.
    """

    def __init__(self, path):
        self.path = path

    def read(self):
        """Method which calls the relevant reading class based on the file name.

        Returns:
            :class:`aprofiles.profiles_data.ProfilesData`

        Example:

            >>> #import library
            >>> import aprofiles as apro
            >>> path = "examples/data/L2_0-20000-001492_A20210909.nc"
            >>> #Initialize reading class with file path
            >>> reader = apro.reader.ReadProfiles(path)
            >>> #calls the read method
            >>> profiles = reader.read()
            >>> print(profiles)
            <aprofiles.profilesdata.ProfilesData object at 0x7f011055fad0>

        """
        
        #get the right reading class
        data = read_eprofile.ReadEPROFILE(self.path).read()
        return ProfilesData(data)

class ReadAeronet:
    """Base class for reading Aeronet data.

    Attributes:
        path (str): path of the file to be read.
    """

    def __init__(self, path):
        self.path = path
        raise NotImplementedError('ReadAeronet class is not implemented yet')

def _main():
    path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
    l2_data = ReadProfiles(path).read()
    print(l2_data)

if __name__ == '__main__':
    _main()
