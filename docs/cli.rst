CLI
============

For facilitating the processing of the measurements in routine, a Command Line Interface (CLI) has been developed: 
:download:`cli/aprocess.py <../cli/aprocess.py>`

In the current version, the CLI has 3 possible actions:

1. process data for all stations via the usual A-Profiles :download:`workflow <../cli/utils/workflow.py>`
2. create a JSON calendar file (used by V-Profiles)
3. create a JSON map file (used by V-Profiles)

Documentation
#############

::

    ./cli/aprocess.py --help

returns the documentation of the CLI, with all available options.

.. code-block:: console
    
    $ ./cli/aprocess.py --help
    Usage: aprocess.py [OPTIONS]

    Run aprofiles standard workflow for given dates, optionally for specific
    instrument types.

    Options:
    --date [%Y-%m-%d]               📅 Processing date.
    --from [%Y-%m-%d]               📅 Initial date
    --to [%Y-%m-%d]                 📅 Ending date.  [default: (Today's date)]
    --today / --no-today            🕑 Process today.  [default: no-today]
    --yesterday / --no-yesterday    🕙 Process yesterday.  [default: no-
                                    yesterday]
    --instruments-type TEXT         📗 List of specific instruments to be
                                    processed.  [default: CHM15k, Mini-MPL]
    --multithread / --no-multithread
                                    ⚡ Use multithread mode.  [default: no-
                                    multithread]
    --basedir-in PATH               📂 Base path for input data.  [default:
                                    data/e-profile]
    --basedir-out PATH              📂 Base path for input data.  [default:
                                    data/v-profiles]
    --update-data / --no-update-data
                                    📈 Update data.  [default: update-data]
    --update-calendar / --no-update-calendar
                                    🗓️ Update calendar.  [default: update-
                                    calendar]
    --update-map / --no-update-map  🗺️ Update map.  [default: update-map]
    --install-completion [bash|zsh|fish|powershell|pwsh]
                                    Install completion for the specified shell.
    --show-completion [bash|zsh|fish|powershell|pwsh]
                                    Show completion for the specified shell, to
                                    copy it or customize the installation.
    --help                          Show this message and exit.

Basic uses
#############

run a specific date
-------------------
::

    ./cli/aprocess.py --date 2021/09/09

run today's files
-----------------
::

    ./cli/aprocess.py --today

run yesterday's files
---------------------
::

    ./cli/aprocess.py --yesterday


More advanced uses
####################

It is possible to combine different options.

run today's and yesterday's files for CHM15k only
-------------------------------------------------
::

    ./cli/aprocess.py --today --yesterday --instruments-type CHM15k

update only calendar files for 2021
-----------------------------------
::

    ./cli/aprocess.py --from 2021-01-01 --to 2021-12-31 --no-update-data --no-update-map



use multithread processing
--------------------------

The data processing can be run in parallel by using the `multithread` option
::

    ./cli/aprocess.py --today --yesterday --multithread