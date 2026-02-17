# Changelog

:material-history:{ style="text-align: center; font-size: xx-large; display: block" }

## 0.15.0
Feb 17, 2026

- Migrate from *poetry* to *uv*.
  
## 0.14.2
Jun 12, 2025

- Create daily climatology files.
  
## 0.14.1
May 22, 2025

- Sort files per *time* and *aer_type* to ensure monotonicity.
  
## 0.14.0
May 21, 2025

- Add *aprofiles* version in output files metadata and as a general option of the *CLI*.
  
## 0.13.3
May 20, 2025

- Make sure files with dimensions in the the order (altitude, time) are computed, and not just lazy processed with *dask*, which made the lowest layers extrapolation not working.
  

## 0.13.2
Mar 24, 2025

- Fix map processing by using new attributes name (`station_altitude_t0`, `station_latitude_t0` and `station_longitude_t0`)
  
## 0.13.1
Mar 24, 2025

- In *CLI*, return PBL under clouds per default

## 0.13.0
Mar 24, 2025

This update intends to support the processing of *moving stations*.

- update `profiles` Object data format
  - the reference altitude is set above ground level (instead of above sea level)
  - add time dimension to `station_altitude`, `station_latitude` and `station_longitude`
- update `AP` files formatting to reflect new `profiles` format
  - add `station_altitude_t0`, `station_latitude_t0` and `station_longitude_t0` attributes for convenience
  
## 0.12.5
Feb 12, 2025

- adjust some parameters in cli workflow
  
## 0.12.4
Feb 11, 2025

- fix *pip* extras dependencies installation

## 0.12.3
Feb 11, 2025

- goes from *groups* to *extras* for dependencies support with pip

## 0.12.2
Feb 11, 2025

- CLI updates:
  - skip corrupted files in calendar and map files making
  - fix some conflicts in climatology due to file format changes
  
## 0.12.1
Feb 10, 2025

- write *cloud_base_height* variable provided in original files
- update documentation

## 0.12.0
Feb 10, 2025

- add [AI-Profiles](https://github.com/AugustinMortier/ai-profiles) Deep Embedded Clustering (DEC) cloud detection method in addition to the vertical gradient (VG). The two methods are available into the cloud detection function. DEC is the default selected method.
- revisit documentation accordingly
- use *snr* method as a fallback to detect fog or condensation if the method is called before the cloud detection
  
> [!WARNING]  
> breaking change: the cloud detection output is now defined into a single *cloud* boolean variable instead of the combination of *bases*, *peaks*, and *tops*, so both cloud detection methods (DEC)

## 0.11.2
Feb 4, 2025

- use *groups* instead of *extras* for dependencies installation

## 0.11.1
Oct 29, 2024

- replace emc (Extinction to Mass Coefficient) to mec (Mass to Extinction Coefficient)
  
## 0.11.0
Oct 29, 2024

- add ifs emc to netcdf files and emc for different aerosol types and ifs to map json files
  
## 0.10.6
Oct 25, 2024

- fix CI

## 0.10.5
Oct 25, 2024

- change `aer_ifs.json` structure
- move config logic to workflow part

## 0.10.4
Oct 19, 2024

- change `lr_ifs.json` to `aer_ifs.json`
  
## 0.10.3
Oct 18, 2024

- use time_steps option (6 by default, for working with 30 minutes batch files)
  
## 0.10.2
Oct 18, 2024

- make 30 minutes batch L2b files

## 0.10.1
Oct 10, 2024

- preserve time dimension in L2B files

## 0.10.0
Oct 10, 2024

- revisit CLI: two commands
    - `apro run` (formerly `aprocess`: run standard workflow)
    - `apro l2b` (creates L2B files out of AP files)

## 0.9.7
Oct 3, 2024

- round up values in climatology files

## 0.9.6
Oct 2, 2024

- fix time unit in climatology files
- fix typo in documentation
  
## 0.9.5
Oct 2, 2024

- write time as int in climatology files
  
## 0.9.4
Oct 2, 2024

- fix typo
  
## 0.9.3
Oct 2, 2024

- add Z as suffix to time in climatology json files

## 0.9.2
Oct 1, 2024

- change snr calculation
- fix build
- sort climatology by time

## 0.9.1
Sep 30, 2024

- fix pip version number
  
## 0.9.0
Sep 30, 2024

- Add `aod` and `lidar_ratio` to climatology files

## 0.8.4
Sep 27, 2024

- Add `lidar_ratio` to maps.json

## 0.8.3
Sep 26, 2024

- Fix time precision (double instead of float)
  
## 0.8.2
Sep 25, 2024

- Fix time precision (double instead of float)
  
## 0.8.1
Sep 24, 2024

- Fix progress bar visibility in CLI climatology
- Only read relevant variables in CLI maps and calendar
- Fix some links in documentation

## 0.8.0
Sep 23, 2024

- Use *mkdocs* for documentation
- Compress all variables when writing AP files
- New logo
- Update README.md

## 0.7.2
Sep 21, 2024

- Update quality flags attrs type for CF compliance.

## 0.7.1
Sep 21, 2024

- Update dependencies
- Fix documentation
- Makes climatology much faster by using dask

## 0.7.0
Sep 20, 2024

- Support Python 3.12.
- Replace *tqdm* with *rich*

## 0.6.5
Sep 20, 2024

- Work on CF compliance (write time as days).

## 0.6.4
Sep 16, 2024

- Work on CF compliance (missing altitude direction and time units).

## 0.6.3
Nov 10, 2023

- Fix time conversion warnings in the map processing.

## 0.6.2
Nov 9, 2023

- Enable multiprocessing for climatology computation.
- Fix bug in map processing due to the removal of time conversion warnings (0.6.1).

## 0.6.1
Nov 9, 2023

CLI improvements:
- Remove time conversion warnings in map computation.
- Add indicator in progress-bar when using multiprocessing.

## 0.6.0
Nov 3, 2023

- Support python3.11.
- Fix relative paths issues occurring when the CLI is triggered without a local copy of the repository (via module load on ecFlow).

## 0.5.15
Nov 3, 2023

- Fix resampling issue [TypeError: Grouper.\_\_init\_\_() got an unexpected keyword argument 'base'] obtained with pandas v2.0.0. See [xarray issue #8282](https://github.com/pydata/xarray/issues/8282).
- Add workers option in the CLI.

## 0.5.14
Mar 24, 2022

- Explicitly add *numba* to the list of required dependencies for solving some installation issues.

## 0.5.13
Dec 2, 2022

- Create a DOI and add [citation file](https://citation-file-format.github.io/) in the Git repository.

## 0.5.12
Nov 16, 2022

- Fix relative path of the config file read in the *CLI* to make the command work properly anywhere.

## 0.5.11
Nov 15, 2022

- Move *CLI* within the package directory to make *aprocess* available everywhere.
- Add *pipx* installation instructions in documentation.

## 0.5.10
Nov 10, 2022

- Create a *aprocess* command (calling `cli/aprocess.py`).
- Update Typer (from 0.4.0 to 0.7.0).
- Use *Path* library.
- Clean up imports.

## 0.5.9
Oct 27, 2022

- Support Python 3.10.

## 0.5.8
Jul 15, 2022

- Fix climatology computation bug, which was returning only a single profile instead of seasonal profiles.
- New configuration file `cfg.json` with a new *exclude_stations_id_from_climatology* key for removing some stations with changing altitude.
- Add a try/except block in the climatology computation for excluding stations with non-monotonic global indexes.

## 0.5.7
Jul 14, 2022

- Remove time duplicates if they exist in the L2 file (e.g., `L2_0-380-61_A20220708.nc`) that were causing conflicts when trying to read multiple files for computing the climatology with `xarray.open_mfdataset`.

## 0.5.6
Jul 13, 2022

- Fix a bug in the PBL detection that was triggering an *IndexError* when no valid point was found in a profile (e.g., `L2_0-20000-003590_A20220701.nc`).
- Improve the previous clouds detection fix, by checking if any valid point was found in the processed profile.

## 0.5.5
Jul 13, 2022

- Fix a bug in the clouds detection that was triggering an *IndexError* when no valid point was found in a profile (e.g., `L2_0-20000-003590_A20220701.nc`).

## 0.5.4
Jul 12, 2022

- Fix a bug in the clouds detection that was triggering an *IndexError* when data presented consecutive equal values vertically (e.g., `L2_0-20000-006432_A20220701.nc` where large squares in the altitude are filled with *NaN* values).

## 0.5.3
Jun 20, 2022

- Update *pydata-sphinx-theme* minimum required version from 0.7.2 to 0.9.0 for supporting dark mode 🌘.
- Update *black* minimum required version from 21.12b0 to 22.3.0.

## 0.5.2
Apr 13, 2022

- Change max valid AOD value used to define outliers from 0.5 to 2.0.

## 0.5.1
Apr 13, 2022

- Add *compat='override'* option to the `update_climatology()` function to resolve potential merging issues.

## 0.5.0
Apr 12, 2022

- Add *\--update-climatology* option in the CLI. This option creates seasonal extinction profiles in one climatology JSON file per station after reading all available AP files.

## 0.4.2
Apr 12, 2022

- Fix *\--from* option in CLI.

## 0.4.1
Jan 31, 2022

- Add *alc_parameters.json* file in CLI config directory for overwriting dataflow parameters for different ALC types.
- Add *\--no-progress-bar* option in CLI.

## 0.4.0
Jan 27, 2022

- Add test suite using *pytest* and *pytest-cov*.

## 0.3.5
Jan 18, 2022

- Enables reading of original CEDA archive files with variables having dimensions as (altitude, time) instead of (time, altitude).

## 0.3.4
Dec 14, 2021

- Exit forward inversion loop as soon as a *np.nan* value is found in the profile.
- Work on documentation.

## 0.3.3
Dec 13, 2021

- Fix *poetry* warning when publishing to *pip*.

> **Note**
>
> After further investigation, the reported issue with the installation of *aprofiles* with *pip* was due to the use of the *-e* option:
>
> - `pip install .` works
> - `pip install . -e` fails

## 0.3.2
Dec 13, 2021

- Use *multiprocessing* instead of *multithreading*.

## 0.3.1
Dec 9, 2021

- Use max altitude as reference altitude when using the forward inversion method.

## 0.3.0
Dec 9, 2021

> **Note**
>
> This version has been removed from *pypi*. Use 0.3.1 instead.

- Fix major bug in the forward inversion method (use of molecular transmission instead of aerosol transmission).
- Use max altitude as reference altitude when using the forward inversion method.
- Add a *simulator* module for computing attenuated backscatter profiles from a given extinction profile model.
- Remove outliers in the standard workflow called by the CLI.

## 0.2.6
Dec 8, 2021

- Fix *Attenuated Backscatter* units from µm⁻¹.sr⁻¹ to Mm⁻¹.sr⁻¹. This bug only impacted figure legends.

## 0.2.5
Dec 7, 2021

- Move *Typer* from development dependencies to default dependencies.

## 0.2.4
Dec 6, 2021

- Remove email address from scripts.
- Change CLI option (instrument-types to instruments-type).
- Add *show_fig* and *save_fig* options to the plotting function.
- Replace *E-6 m⁻¹* by *µm⁻¹* in figures.
- Update README and documentation figures.

## 0.2.3
Dec 3, 2021

- Rename *run* directory to *cli*.
- Rename *aprorun.py* to *aprocess.py*.
- Add CLI documentation.

## 0.2.2
Nov 30, 2021

- Work on CLI:
    - Use [Typer](https://typer.tiangolo.com/) instead of [argparse](https://docs.python.org/3/library/argparse.html/).
    - Use [pathlib](https://docs.python.org/3/library/pathlib.html/) instead of [os.path](https://docs.python.org/3/library/os.path.html/).

## 0.2.1
Nov 29, 2021

- Add CLI for facilitating deployment on ecFlow.

    Examples:
    ```bash
    ./run/aprorun.py --date 2021-09-09
    ./run/aprorun.py --from 2021-09-09 --to 2021-09-10
    ./run/aprorun.py --today
    ./run/aprorun.py --today --yesterday
    ```


## 0.2.0
Nov 19, 2021

-   Initial release

## 0.1.0
Sep 20, 2021

-   Test release
