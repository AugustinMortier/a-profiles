# @author Augustin Mortier
# @desc A-Profiles - Reader class

from aprofiles.io import read_aeronet, read_eprofile
from aprofiles.profiles import ProfilesData


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
            :class:`aprofiles.profiles.ProfilesData`

        Example:
            >>> # import library
            >>> import aprofiles as apro
            >>> path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
            >>> # initialize reading class with file path
            >>> reader = apro.reader.ReadProfiles(path)
            >>> # calls the read method
            >>> profiles = reader.read()
            >>> # print ProfilesData object
            >>> print(profiles)
            <aprofiles.profiles.ProfilesData object at 0x7f011055fad0>
            >>> # print the content of this ProfilesData object
            >>> profiles.__dict__
            {'_data': <xarray.Dataset>
            Dimensions:                          (altitude: 511, layer: 3, time: 273)
            Coordinates:
            * time                             (time) datetime64[ns] 2021-09-09T00:00:04 ... 2021-09-09T23:55:06
            * altitude                         (altitude) float64 111.0 ... 1.541e+04
            Dimensions without coordinates: layer
            Data variables:
                start_time                       (time) datetime64[ns] ...
                latitude                         (time, altitude) float64 ...
                longitude                        (time, altitude) float64 ...
                attenuated_backscatter_0         (time, altitude) float64 ...
                uncertainties_att_backscatter_0  (time, altitude) float64 ...
                l0_wavelength                    float64 1.064e+03
                station_longitude                float64 ...
                station_latitude                 float64 ...
                station_altitude                 float64 ...
                quality_flag                     (time, altitude) int64 ...
                vertical_visibility              (time) float64 ...
                cloud_base_height                (time, layer) float64 ...
                cbh_uncertainties                (time, layer) float64 ...
                cloud_amount                     (time) float64 ...
                calibration_constant_0           (time) float64 ...
            Attributes:
                instrument_id:                A
                hermes_history:               hermes-raw2l1 2.0.1, hermes-eprofile-alc-sc...
                instrument_type:              CHM15k
                site_location:                OSLO,NORWAY
                title:                        OSLO nimbus MET NORWAY
                principal_investigator:       Remote Sensing Group
                optical_module_id:            TUB110019
                comment:                      
                Conventions:                  CF-1.7, UKMO-1.0.2
                wigos_station_id:             0-20000-0-01492
                source:                       Ground Based Remote Sensing
                references:                   E-PROFILE Data Format Description Document
                wmo_id:                       01492
                overlap_is_corrected:         true
                instrument_firmware_version:  1.04
                overlap_function:             true
                institution:                  MET NORWAY Remote Sensing Group
                instrument_serial_number:     TUB110019
                history:                      Thu Sep  9 00:30:28 2021: ncpdq -O -a time,...
                NCO:                          netCDF Operators version 4.9.1 (Homepage = ...}
        """

        # get the right reading class
        data = read_eprofile.ReadEPROFILE(self.path).read()

        # instantitate ProfilesData class with data
        profiles = ProfilesData(data)

        return profiles


class ReadAeronet:
    """Base class for reading Aeronet data.

    Attributes:
        path (str): path of the file to be read.
    """

    def __init__(self, path):
        self.path = path
        raise NotImplementedError("ReadAeronet class is not implemented yet")


def _main():
    path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
    profiles = ReadProfiles(path).read()
    print(profiles)
    print(profiles.data.time)


if __name__ == "__main__":
    _main()
