# @author Augustin Mortier
# @desc A-Profiles - Standard workflow

import aprofiles as apro
from pathlib import Path
import json
import warnings


def workflow(path, instruments_types, base_dir, CFG, verbose=False):
    apro_reader = apro.reader.ReadProfiles(path)
    profiles = apro_reader.read()

    nans = int(profiles.data.attenuated_backscatter_0.isnull().sum())
    total = profiles.data.attenuated_backscatter_0.size
    if (
        int(profiles.data.attenuated_backscatter_0.isnull().sum())
        / profiles.data.attenuated_backscatter_0.size
        >= 0.25
    ):
        warnings.warn(
            f"Error with {path}. attenuated_backscatter_0 variable has {nans}/{total} values as NaNs."
        )
        return

    # do the rest if instrument_type in the list
    if profiles.data.attrs["instrument_type"] in instruments_types:

        # extrapolation lowest layers
        profiles.extrapolate_below(z=260.0, inplace=True)

        # cloud detection
        if "cloud" in CFG["parameters"][profiles.data.instrument_type]:
            if "method" in CFG["parameters"][profiles.data.instrument_type]["cloud"]:
                cloud_method = CFG["parameters"][profiles.data.instrument_type][
                    "cloud"
                ]["method"]
            profiles.clouds(
                cloud_method,
                time_avg=1,
                zmin=300.0,
                thr_noise=5.0,
                thr_clouds=4.0,
                verbose=verbose,
            )

        # foc and pbl
        profiles.foc(zmin_cloud=300.0)
        profiles.pbl(
            zmin=300.0, zmax=3000.0, under_clouds=True, min_snr=1.5, verbose=verbose
        )

        # retrievals
        # inversion method selection
        # 1. default: forward, 50sr
        inversion_method = "forward"
        apriori = {"lr": 50, "mec": False, "use_cfg": False}
        # 2. if exist, overwrite with CFG["parameters"]
        var_apriori = CFG["parameters"][profiles.data.instrument_type]["inversion"][
            "apriori"
        ]["var"]
        if profiles.data.instrument_type in CFG["parameters"]:
            if (
                "cfg"
                in CFG["parameters"][profiles.data.instrument_type]["inversion"][
                    "apriori"
                ]
            ):
                cfg_path = CFG["parameters"][profiles.data.instrument_type][
                    "inversion"
                ]["apriori"]["cfg"]
                # open config
                f = open(Path(Path(__file__).parent, "..", "..", cfg_path))
                aer_ifs = json.load(f)
                f.close()
                station_id = f'{profiles._data.attrs["wigos_station_id"]}-{profiles._data.attrs["instrument_id"]}'
                if station_id in aer_ifs:
                    apriori = {
                        var_apriori: aer_ifs[station_id][var_apriori],
                        "use_cfg": True,
                        "cfg": {
                            "data": aer_ifs[station_id]["data"],
                            "use_default": "False",
                            "attributes": aer_ifs["attributes"],
                            "path": cfg_path,
                        },
                    }
                    if aer_ifs[station_id]["mec"]:
                        apriori["mec"] = aer_ifs[station_id]["mec"]
                else:
                    apriori = {
                        var_apriori: aer_ifs["attributes"]["default"][var_apriori],
                        "use_cfg": True,
                        "cfg": {
                            "use_default": "True",
                            "attributes": aer_ifs["attributes"],
                            "path": cfg_path,
                        },
                    }
                    if aer_ifs["attributes"]["default"]["mec"]:
                        apriori["mec"] = aer_ifs["attributes"]["default"]["mec"]

            if "inversion" in CFG["parameters"][profiles.data.instrument_type]:
                if (
                    "method"
                    in CFG["parameters"][profiles.data.instrument_type]["inversion"]
                ):
                    inversion_method = CFG["parameters"][profiles.data.instrument_type][
                        "inversion"
                    ]["method"]

        profiles.inversion(
            zmin=4000.0,
            zmax=6000.0,
            remove_outliers=True,
            method=inversion_method,
            apriori=apriori,
            verbose=verbose,
        )
        profiles.write(base_dir)
