# @author Augustin Mortier
# @desc A-Profiles - Standard workflow

import aprofiles as apro
import warnings

def workflow(path, instrument_types, base_dir, verbose=False):
    apro_reader = apro.reader.ReadProfiles(path)
    profiles = apro_reader.read()

    nans = int(profiles.data.attenuated_backscatter_0.isnull().sum())
    total = profiles.data.attenuated_backscatter_0.size
    if int(profiles.data.attenuated_backscatter_0.isnull().sum())/profiles.data.attenuated_backscatter_0.size>=0.25:
        warnings.warn(f"Error with {path}. attenuated_backscatter_0 variable has {nans}/{total} values as NaNs.")
        return

    #print(profiles.data.attrs['wigos_station_id'], profiles.data.attrs['instrument_type'], profiles.data.attrs['instrument_type'] in instrument_types)
    # do the rest if instrument_type in the list
    if profiles.data.attrs['instrument_type'] in instrument_types:

        # extrapolation lowest layers
        profiles.extrapolate_below(z=150., inplace=True)

        # detection
        profiles.foc(zmin_cloud=250.)
        profiles.clouds(zmin=250., thr_noise=5., thr_clouds=4., verbose=verbose)
        profiles.pbl(zmin=200., zmax=3000., under_clouds=False, min_snr=1., verbose=verbose)

        # retrievals
        profiles.inversion(zmin=4000., zmax=6000., remove_outliers=False, method="forward", verbose=verbose)
        profiles.write(base_dir)
