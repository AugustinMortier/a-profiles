#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles - Reader class

import xarray as xr

from aprofiles.profilesdata import ProfilesData


class ReadProfiles:
    """Base class for reading profile data.

    Attributes:
        path (str): path or URL of the file to be read.
    """

    def __init__(self, path):
        self.path = path

    def _get_reader(self):
        """Method which gets the right reader class.

        Note:
            Based on the file name, we return the relevant reading class.

        Returns:
            :class:`__main__._ReadL2EPROFILE`: reader class
        """

        #check if the filename starts with L2
        filename = self.path.split('/')[-1]
        if filename[0:2] == 'L2':
            return _ReadL2EPROFILE
        else:
            raise NotImplementedError('Only L2 files are supported at the moment')

    def read(self):
        """Method which calls the relevant reading class based on the file name.

        Returns:
            :class:`aprofiles.Profiles`: Profiles object

        Example:

            >>> #import library
            >>> import aprofiles as apro
            
            >>> #Initialize reading class with file path
            >>> path = "examples/data/L2_0-20000-001492_A20210909.nc"
            >>> reader = apro.ReadProfiles(path)

            >>> #calls the read method
            >>> profiles = reader.read()
            
        """
        
        #get the right reading class
        reading_class = self._get_reader()
        #calls the read function from the right reading class
        data = reading_class(self.path).read_file()

        return ProfilesData(data)

class _ReadL2EPROFILE:
    """Read Level 2 data E-PROFILE single NetCDF file.
    
    Note:
        This function can also fetch data from the E-PROFILE hub:
        https://data.ceda.ac.uk/badc/eprofile/data/
        https://data.ceda.ac.uk/badc/eprofile/data/daily_files/

    Attributes:
        path (str): The path of the file to be read (path or URL).

    Returns:
        <class 'xarray.Dataset'>
    """

    def __init__(self, path):
        self.path = path

    def check_path(self):
        """Check the path

        Raises:
            OSError: [description]
            NotImplementedError: [description]
        """
        #check if file is NetCDF
        filename = self.path.split('/')[-1]
        if filename[-3:] != '.nc':
            raise OSError("NetCDF: Unknown file format:{}".format(filename))
        #check if web address
        if self.path[0:5] == 'https':
            raise NotImplementedError("The reading of CEDA Archive is not implemented yet")

    def read_file(self):
        self.check_path()
        dataset = xr.open_dataset(self.path)
        return dataset


def _main():
    path = "examples/data/L2_0-20000-001492_A20210909.nc"
    l2_data = ReadProfiles(path).read()
    print(l2_data)

if __name__ == '__main__':
    _main()
