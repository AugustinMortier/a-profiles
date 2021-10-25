#!/usr/bin/env python3

# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles - Mass Concentration

import json

import aprofiles as apro
import numpy as np
import xarray as xr


def concentration_profiles(self, method):
    """Calculates Mass concentration profiles for different aerosol types

    Args:
        - method ({'mortier_2013','literature'}): method for calculating EMC

    Returns:
        :class:`aprofiles.profiles.ProfilesData` object with additional :class:`xarray.Dataset`.
            - `'mass_concentration:<aer_type>'`

    Example:
        Profiles preparation

        >>> import aprofiles as apro
        >>> # read example file
        >>> path = "examples/data/L2_0-20000-001492_A20210909.nc"
        >>> reader = apro.reader.ReadProfiles(path)
        >>> profiles = reader.read()
        >>> # extrapolate lowest layers
        >>> profiles.extrapolate_below(z=150, inplace=True)

        Forward inversion

        >>> # aerosol inversion
        >>> profiles.inversion(zmin=4000, zmax=6000, remove_outliers=False, method='forward', method_mass_conc='mortier_2013')
        >>> # plot mass concentration profiles for urban particles
        >>> profiles.plot(var='mass_concentration:urban', zmax=6000, vmin=0, vmax=50)

        .. figure:: ../../examples/images/mass_conc-urban.png
            :scale: 50 %
            :alt: mass concentration

            Mass concentration profiles in the case of urban particles.

    """

    # read aer_properties.json files
    f = open("aprofiles/config/aer_properties.json")
    aer_properties = json.load(f)
    f.close()
    # check if the aer_type exist in the json file
    aer_types = aer_properties.keys()

    # get wavelength
    wavelength = float(self.data.l0_wavelength.data)
    if self.data.l0_wavelength.units != "nm":
        raise ValueError("wavelength units is not `nm`.")

    for aer_type in aer_types:
        # calculates emc
        emc = apro.emc.EMCData(aer_type, wavelength, method)

        # compute mass_concentration profile
        mass_concentration = self.data.extinction
        # mass_concentration = copy.deepcopy(self.data.extinction)
        mass_concentration.data = np.divide(mass_concentration, emc.emc)
        # # conversion from g.m-3 to µg.m-3
        # mass_concentration.data = mass_concentration.data*1e6

        # creates dataset with a dataarray for each aer_type
        self.data["mass_concentration:{}".format(aer_type)] = xr.DataArray(
            data=mass_concentration.data,
            dims=["time", "altitude"],
            coords=dict(time=self.data.time.data, altitude=self.data.altitude.data),
            attrs=dict(
                long_name="Mass concentration [{} particles]".format(
                    aer_type.replace("_", " ")
                ),
                units="µg.m-3",
                emc=emc.emc,
            ),
        )
    return self


def _main():
    import aprofiles as apro

    path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
    profiles = apro.reader.ReadProfiles(path).read()

    # basic corrections
    profiles.extrapolate_below(z=150.0, inplace=True)
    profiles.inversion(verbose=True, mass_conc_method="mortier_2013")
    profiles.plot("mass_concentration:urban", zmax=6000, vmin=0, vmax=10)


if __name__ == "__main__":
    _main()
