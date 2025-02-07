# @author Augustin Mortier
# @desc A-Profiles - Mass Concentration

import json

import aprofiles as apro
import numpy as np
from pathlib import Path


def concentration_profiles(profiles, method, apriori):
    """Calculates Mass concentration profiles for different aerosol types

    Args:
        profiles (aprofiles.profiles.ProfilesData): `ProfilesData` instance.
        method (str): Method for calculating MEC. Must be one of {"mortier_2013", "literature"}.
        apriori (dict): Apriori mec value (m2.g-1).

    Returns:
        (aprofiles.profiles.ProfilesData):
            object with additional (xarray.Dataset):

            - `'mass_concentration:<aer_type>'`

    Example:
        Profiles preparation
        ```python
        import aprofiles as apro
        # read example file
        path = "examples/data/L2_0-20000-001492_A20210909.nc"
        reader = apro.reader.ReadProfiles(path)
        profiles = reader.read()
        # extrapolate lowest layers
        profiles.extrapolate_below(z=150, inplace=True)
        ```

        Forward inversion
        ```python
        # aerosol inversion
        profiles.inversion(
            zmin=4000, zmax=6000, remove_outliers=False, method='forward', 
            method_mass_conc='mortier_2013'
        )
        # plot mass concentration profiles for urban particles
        profiles.plot(var='mass_concentration:urban', zmax=6000, vmin=0, vmax=100)
        ```

        ![Mass concentration profiles in the case of urban particles](../../assets/images/mass_conc-urban.png)
    """

    # read aer_properties.json files
    f = open(Path(Path(__file__).parent,'..','config','aer_properties.json'))
    aer_properties = json.load(f)
    f.close()
    # check if the aer_type exist in the json file
    aer_types = aer_properties.keys()

    # get wavelength
    wavelength = float(profiles.data.l0_wavelength.data)
    if profiles.data.l0_wavelength.units != "nm":
        raise ValueError("wavelength units is not `nm`.")

    for aer_type in aer_types:
        # calculates mec
        mec = apro.mec.MECData(aer_type, wavelength, method)

        # compute mass_concentration profile. Use extinction as base.
        mass_concentration = profiles.data.extinction * 1e-3 #conversion from km-1 to m-1
        # mass_concentration = copy.deepcopy(profiles.data.extinction)
        mass_concentration.data = np.divide(mass_concentration, mec.mec)
        # # conversion from g.m-3 to µg.m-3
        mass_concentration.data = mass_concentration.data * 1e6

        # creates dataset with a dataarray for each aer_type
        profiles.data[f"mass_concentration:{aer_type}"] = (('time', 'altitude'), mass_concentration.data)
        profiles.data[f"mass_concentration:{aer_type}"] = profiles.data[f"mass_concentration:{aer_type}"].assign_attrs({
            'long_name': f"Mass concentration [{aer_type.replace('_', ' ')} particles]",
            'units': 'µg.m-3',
            'mec': mec.mec,
        })
    
    # add ifs mec
    if apriori.get("mec"):
        aer_type = "ifs"
        # compute mass_concentration profile. Use extinction as base.
        mass_concentration = profiles.data.extinction * 1e-3 #conversion from km-1 to m-1
        # mass_concentration = copy.deepcopy(profiles.data.extinction)
        mass_concentration.data = np.divide(mass_concentration, apriori["mec"])
        # # conversion from g.m-3 to µg.m-3
        mass_concentration.data = mass_concentration.data * 1e6

        # creates dataset with a dataarray for each aer_type
        profiles.data[f"mass_concentration:{aer_type}"] = (('time', 'altitude'), mass_concentration.data)
        profiles.data[f"mass_concentration:{aer_type}"] = profiles.data[f"mass_concentration:{aer_type}"].assign_attrs({
            'long_name': f"Mass concentration [{aer_type.replace('_', ' ')}]",
            'units': 'µg.m-3',
            'mec': apriori["mec"],
        })
        
    return profiles


def _main():
    import aprofiles as apro

    path = "examples/data/E-PROFILE/L2_0-20000-001492_A20210909.nc"
    profiles = apro.reader.ReadProfiles(path).read()

    # basic corrections
    profiles.extrapolate_below(z=150.0, inplace=True)
    profiles.inversion(verbose=True, mass_conc_method="mortier_2013")
    profiles.plot("mass_concentration:urban", zmax=6000, vmin=0, vmax=100)


if __name__ == "__main__":
    _main()
