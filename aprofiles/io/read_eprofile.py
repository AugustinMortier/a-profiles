#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles - E-PROFILE reading class

import xarray as xr


class ReadEPROFILE:
    """E-PROFILE reading class.

    Data:
        [https://data.ceda.ac.uk/badc/eprofile/data/daily_files/]

    Attributes:
        path (str): The path of the file to be read (path or URL).
    """

    def __init__(self, path):
        self.path = path

    def _check_path(self):
        """Check the path

        Raises:
            OSError: [description]
            NotImplementedError: [description]
        """
        # check if file is NetCDF
        filename = self.path.split("/")[-1]
        if filename[-3:] != ".nc":
            raise OSError("NetCDF: Unknown file format:{}".format(filename))
        # check if web address
        if self.path[0:5] == "https":
            raise NotImplementedError(
                "The reading of CEDA Archive is not implemented yet"
            )

    def _read_l2file(self):
        """Read single file using `xr.open_dataset()`.

        Returns:
            :class:`xarray.Dataset`
        """
        dataset = xr.open_dataset(self.path)
        # replace wavelength with actual value in attenuated backscatter longname
        dataset.attenuated_backscatter_0.attrs[
            "long_name"
        ] = dataset.attenuated_backscatter_0.long_name.replace(
            "at wavelength 0", "@ {} nm".format(int(dataset.l0_wavelength.data))
        )
        dataset.attenuated_backscatter_0.attrs[
            "units"
        ] = dataset.attenuated_backscatter_0.attrs["units"].replace(
            "1E-6*1/(m*sr)", ("E-6 m-1.sr-1")
        )

        return dataset

    def read(self):
        self._check_path()
        """Method which reads E-PROFILE data.

        Returns:
            :class:`xarray.Dataset`
        """

        # check if the filename starts with L2
        filename = self.path.split("/")[-1]
        if filename[0:2] == "L2":
            return self._read_l2file()
        else:
            raise NotImplementedError("Only L2 files are supported at the moment")
