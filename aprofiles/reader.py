#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles Reader

import urllib.request
import io
import xarray as xr

class ReadProfiles:
    """Class for reading vertical profiles.

    Note:
        Do not include the `self` parameter in the ``Args`` section.

    Attributes:
        path (str): path of path of the file to be read.
    """

    def __init__(self, path):
        self.path = path

    def _get_reader(self):
        """Method which gets the right reader class.

        Note:
            Based on the file name, we return the relevant reading class.

        Returns:
            <class '__main__._ReadL2EPROFILE'>: reader class
        """

        #check if the filename starts with L2
        filename = self.path.split('/')[-1]
        if filename[0:2] == 'L2':
            return _ReadL2EPROFILE
        else:
            raise NotImplementedError('Only L2 files are supported at the moment')

    def read(self):
        """Method which calls the relevant reading class.

        Note:
            Based on the file name, we call the relevant reading class.

        Returns:
            <class 'xarray.Dataset'>: xarray Dataset
        """
        
        #get the right reading class
        reading_class = self._get_reader()
        #calls the read function from the right reading class
        data = reading_class(self.path).read_file()
        return data

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


def main():
    #path = "https://dap.ceda.ac.uk/badc/eprofile/data/norway/oslo/met-norway-jenoptick-chm15k-nimbus_A/2021/06/26/L2_0-20000-0-01492_A202106260005.nc"
    path = "data/e-profile/2021/09/08/L2_0-20000-006735_A20210908.nc"
    #path = "tests/data/test.txt"
    l2_data = ReadProfiles(path).read()
    print(l2_data)

if __name__ == '__main__':
    main()