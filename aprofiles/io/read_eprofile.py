# @author Augustin Mortier
# @desc A-Profiles - E-PROFILE reading class

import numpy as np
import xarray as xr


class ReadEPROFILE:
    """
    E-PROFILE reading class.

    Data:
        [https://data.ceda.ac.uk/badc/eprofile/data/daily_files/]

    Attributes:
        path (str): The path of the file to be read (path or URL).
    """

    def __init__(self, path):
        self.path = path

    def _check_path(self):
        """
        Check the path

        Raises:
            OSError: [description]
            NotImplementedError: [description]
        """
        # check if file is NetCDF
        filename = self.path.split("/")[-1]
        if not filename.endswith(".nc"):
            raise OSError(
                f"NetCDF file required (.nc). File format not supported {filename}"
            )
        # check if web address
        if self.path.startswith("https://"):
            raise NotImplementedError(
                "The reading of CEDA Archive is not implemented yet"
            )

    def _read_l2file(self):
        """
        Read single file using `xr.open_dataset()`.

        Returns:
            (xarray.Dataset):
        """
        ds = xr.open_dataset(self.path, decode_times=True)
        # remove time duplicate values if exists
        if len(ds.time.values) != len(np.unique(ds.time.values)):
            ds = ds.drop_duplicates(dim="time")
        # in CEDA archive, dimensions come as (altitude, time). Transpose all variables which have altitude as dimension.
        if ds.latitude.dims[0] == "altitude":
            ds = ds.transpose(..., "altitude").compute()

        # make sure that the station_altitude variable follows the time dimension
        position_keys = ["station_latitude", "station_longitude", "station_altitude"]
        for position_key in position_keys:
            if type(ds[position_key].data.tolist()) == float:
                if (
                    position_key == "station_altitude"
                    and ds.altitude.long_name == "Altitude above sea level"
                ):
                    # Store existing attributes
                    altitude_attrs = ds.altitude.attrs
                    ds = ds.assign_coords(
                        altitude=np.round(ds.altitude - ds[position_key].data, 3)
                    )
                    altitude_attrs["long_name"] = "Altitude above ground level"
                    ds["altitude"] = ds.altitude.assign_attrs(altitude_attrs)

                altitude_array = np.ones(np.shape(ds.time.data)) * ds[position_key].data
                ds[position_key] = xr.DataArray(
                    data=altitude_array, dims=["time"], coords={"time": ds.time}
                )

        # replace wavelength with actual value in attenuated backscatter longname
        ds.attenuated_backscatter_0.attrs["long_name"] = (
            ds.attenuated_backscatter_0.long_name.replace(
                "at wavelength 0", f"@ {int(ds.l0_wavelength.data)} nm"
            )
        )
        ds.attenuated_backscatter_0.attrs["units"] = ds.attenuated_backscatter_0.attrs[
            "units"
        ].replace("1E-6*1/(m*sr)", ("Mm-1.sr-1"))
        return ds

    def read(self):
        """
        Method which reads E-PROFILE data.

        Returns:
            (xarray.Dataset):
        """

        self._check_path()

        # check if the filename starts with L2
        filename = self.path.split("/")[-1]
        if filename.startswith("L2"):
            return self._read_l2file()
        else:
            raise NotImplementedError("Only L2 files are supported at the moment")
