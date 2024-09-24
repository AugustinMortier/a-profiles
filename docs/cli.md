# CLI

:material-keyboard:

For facilitating the processing of the measurements in routine, a
Command Line Interface (CLI) has been developed:
[cli/aprocess.py](cli/aprocess.py){: .download}

In the current version, the CLI has 3 possible actions:

1.  process data for all stations via the usual A-Profiles [cli/utils/workflow.py](cli/utils/workflow.py){: .download}
2.  create a JSON calendar file (used by V-Profiles)
3.  create a JSON map file (used by V-Profiles)

## Installation

In order to use the CLI, A-Profiles needs to be installed with the
required extras:

:simple-pipx: via *pip/pipx*

```
pip install .[cli]
```

:simple-poetry: via *poetry*

```
poetry install --extras cli
```

## Documentation

    aprocess --help

returns the documentation of the CLI, with all available options.

```
$ aprocess --help


Usage: aprocess [OPTIONS]                                                                                                                                    

Run aprofiles standard workflow for given dates, optionally for specific instruments types.                                                                  
See some examples here: https://a-profiles.readthedocs.io/en/latest/cli.html                                                                                 

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --date                                             [%Y-%m-%d]              📅 Processing date.                                                                                       │
│ --from                                             [%Y-%m-%d]              📅 Initial date. [default: None]                                                                          │
│ --to                                               [%Y-%m-%d]              📅 Ending date. [default: (Today's date)]                                                                 │
│ --today                 --no-today                                         🕑 Process today's data. [default: no-today]                                                              │
│ --yesterday             --no-yesterday                                     🕙 Process yesterday's data. [default: no-yesterday]                                                      │
│ --instruments-type                                 [CHM15k|Mini-MPL|CL61]  📗 List of specific instruments to be processed. [default: CHM15k, Mini-MPL]                              │
│ --multiprocessing       --no-multiprocessing                               🚀 Use multiprocessing mode. [default: no-multiprocessing]                                                │
│ --workers                                          INTEGER RANGE [x>=1]    👷 Number of workers (NSLOTS, if multiprocessing mode is enabled). [env var: NSLOTS] [default: 2]         │
│ --basedir-in                                       PATH                    📂 Base path for input data. [default: data/e-profile]                                                    │
│ --basedir-out                                      PATH                    📂 Base path for output data. [default: data/v-profiles]                                                  │
│ --update-data           --no-update-data                                   📈 Update data. [default: update-data]                                                                    │
│ --update-calendar       --no-update-calendar                               🗓️ Update calendar. [default: update-calendar]                                                            │
│ --update-map            --no-update-map                                    🗺️ Update map. [default: update-map]                                                                      │
│ --update-climatology    --no-update-climatology                            ↪️ Update climatology. [default: update-climatology]                                                       │
│ --progress-bar          --no-progress-bar                                  ⌛ Show progress bar. [default: progress-bar]                                                             │
│ --install-completion                                                       Install completion for the current shell.                                                                 │
│ --show-completion                                                          Show completion for the current shell, to copy it or customize the installation.                          │
│ --help                                                                     Show this message and exit.                                                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Basic uses

### run a specific date

```
aprocess --date 2021-09-09
```

### run today\'s files

```
aprocess --today
```

### run yesterday\'s files

```
aprocess --yesterday
```

## More advanced uses

It is possible to combine different options.

### run today\'s and yesterday\'s files for CHM15k only

```
aprocess --today --yesterday --instruments-type CHM15k
```

### update only calendar files for 2021

```
aprocess --from 2021-01-01 --to 2021-12-31 --no-update-data --no-update-map
```

### use multiprocessing

The data processing can be run in parallel by using the
[`multiprocessing`] option :
```
aprocess --today --yesterday --multiprocessing
```
