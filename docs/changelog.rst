Changelog
============

.. image:: _static/images/history-solid.svg
   :class: awesome-svg

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
