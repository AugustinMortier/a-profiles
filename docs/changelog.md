# Changelog

:material-history:{ style="text-align: center; font-size: xx-large; display: block" }

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
