Changelog
============

.. image:: _static/images/history-solid.svg
   :class: awesome-svg

0.5.14
^^^^^^^
Mar 24, 2022

- Explicitely add `numba` to the list of required dependencies for solving some installation issues.

0.5.13
^^^^^^^
Dec 2, 2022

- Create a doi and add `citation file <https://citation-file-format.github.io/>`_ in Git repository.

0.5.12
^^^^^^^
Nov 16, 2022

- Fix relative path of the config file read in the *CLI* to make the command work properly anywhere.


0.5.11
^^^^^^^
Nov 15, 2022

- Move *CLI* within package directory to make `aprocess` available everywhere.
- Add *pipx* installation instructions in documentation.

0.5.10
^^^^^^^
Nov 10, 2022

- Create a *aprocess* command (calling `cli/aprocess.py`).
- Update Typer (from 0.4.0 to 0.7.0).
- Use *Path* library.
- Clean up imports.

0.5.9
^^^^^^^
Oct 27, 2022

- Support Python 3.10.

0.5.8
^^^^^^^
Jul 15, 2022

- Fix climatology computation bug, which was returning only a single profile instead of seasonal profiles.
- New configuration file `cfg.json` with a new *exclude_stations_id_from_climatology* key for removing some stations with changing altitude.
- Add a try/except block in the climatology computation for excluding stations with non monotonic global indexes.

0.5.7
^^^^^^^
Jul 14, 2022

- Remove time duplicates if they exist in the L2 file (e.g: *L2_0-380-61_A20220708.nc*) that were causing conflicts when trying to read multiple files for computing the climatology with `xarray.open_mfdataset`.

0.5.6
^^^^^^^
Jul 13, 2022

- Fix a bug in the PBL detection that was triggering an *IndexError* when no valid point was found in a profile (e.g: *L2_0-20000-003590_A20220701.nc*).
- Improve the previous clouds detection fix, by checking if any valid point was found in the processed profile.

0.5.5
^^^^^^^
Jul 13, 2022

- Fix a bug in the clouds detection that was triggering an *IndexError* when no valid point was found in a profile (e.g: *L2_0-20000-003590_A20220701.nc*).

0.5.4
^^^^^^^
Jul 12, 2022

- Fix a bug in the clouds detection that was triggering an *IndexError* when data present consecutive equal values vertically (e.g: *L2_0-20000-006432_A20220701.nc* where large squares(time, altitude) are filled with *NaN* values).

0.5.3
^^^^^^^
Jun 20, 2022

- Update *pydata-sphinx-theme* minimum required version from 0.7.2 to 0.9.0 for supporting dark mode 🌘.
- Update *black* minimum required version from 21.12b0 -> 22.3.0.

0.5.2
^^^^^^^
Apr 13, 2022

- Change max valid AOD value used to define outliers from 0.5 to 2.0.

0.5.1
^^^^^^^
Apr 13, 2022

- Add *compat='override'* option update_climatology function for resolving potential merging issues.

0.5.0
^^^^^^^
Apr 12, 2022

- Add *--update-climatology* option in CLI. This option creates seasonal extinction profiles in one climatology json file per station after reading all AP files available.

0.4.2
^^^^^^^
Apr 12, 2022

- Fix *--from* option in CLI.

0.4.1
^^^^^^^
Jan 31, 2022

- Add *alc_parameters.json* file in CLI config directory for overwriting dataflow parameters for different ALC types.
- Add *--no-progress-bar* option in CLI.

0.4.0
^^^^^^^
Jan 27, 2022

- Add test suite using *pytest* and *pytest-cov*.

0.3.5
^^^^^^^
Jan 18, 2022

- Enables reading of original CEDA archive files with variables having dimensions as (altitude, time) instead of (time, altitude).


0.3.4
^^^^^^^
Dec 14, 2021

- Exit forward inversion loop as soon as a *np.nan* value is found in the profile.
- Work on documentation.

0.3.3
^^^^^^^
Dec 13, 2021

- Fix *poetry* warning when publishing to *pip*.

.. note::
    After further investigation, the reported issue with the installation of *aprofiles* with *pip* was due to the use of *-e* option:
    
    - `pip install .` works
    - `pip install . -e` fails

0.3.2
^^^^^^^
Dec 13, 2021

- Use *multiprocessing* instead of *multithread*.

0.3.1
^^^^^^^
Dec 9, 2021

- Use max altitude as reference altitude when using the forward inversion method.

0.3.0
^^^^^^^
Dec 9, 2021

.. note::
    This version has been removed from *pypi*. Use 0.3.1 instead.

- Fix major bug in *forward* inversion method (use of molecular transmission instead of aerosol transmission).
- Use max altitude as reference altitude when using the forward inversion method.
- Add a *simulator* module for computing attenuated backscatter profiles from a given extinction profile model.
- Remove outliers in standard workflow called by the CLI.

0.2.6
^^^^^^^
Dec 8, 2021

- Fix *Attenuated Backscatter* units from µm-1.sr-1 to Mm-1.sr-1. This bug only impacted figures legends.

0.2.5
^^^^^^^
Dec 7, 2021

- Move *Typer* from development dependencies to default dependencies

0.2.4
^^^^^^^
Dec 6, 2021

- Remove email address from scripts
- Change CLI option (instrument-types to instruments-type)
- Add *show_fig* and *save_fig* options to plotting function
- Replace *E-6 m-1* by *µm-1* in figures
- Update README and documentation figures

0.2.3
^^^^^^^
Dec 3, 2021

- Rename *run* directory to *cli*
- Rename *aprorun.py* to *aprocess.py*
- Add CLI documentation

0.2.2
^^^^^^^
Nov 30, 2021

- Work on CLI: 
    - Use `Typer <https://typer.tiangolo.com/>`_ instead of `argparse <https://docs.python.org/3/library/argparse.html/>`_
    - Use `pathlib <https://docs.python.org/3/library/pathlib.html/>`_ instead of `os.path <https://docs.python.org/3/library/os.path.html/>`_


0.2.1
^^^^^^^
Nov 29, 2021

- Add CLI for facilitating deployment on ecFlow 

e.g:
    - ``./run/aprorun.py --date 2021-09-09``
    - ``./run/aprorun.py --from 2021-09-09 --to 2021-09-10``
    - ``./run/aprorun.py --today``
    - ``./run/aprorun.py --today --yesterday``

0.2.0
^^^^^^^
Nov 19, 2021

- Initial release


0.1.0
^^^^^^^
Sep 20, 2021

- Test release
