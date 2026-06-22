# CLI

:material-keyboard:{ style="text-align: center; font-size: xx-large; display: block" }

For facilitating the processing of the measurements in routine, a
Command Line Interface (CLI) has been developed:
[cli/apro.py](cli/apro.py){: .download}

In the current version, the CLI has 3 possible actions:

1.  process data for all stations via the usual A-Profiles [cli/utils/workflow.py](cli/utils/workflow.py){: .download}
2.  create a JSON calendar file (used by V-Profiles)
3.  create a JSON map file (used by V-Profiles)

## Installation

In order to use the CLI, A-Profiles needs to be installed with the
required extras:

:simple-pipx: via *pip/pipx*

``` bash
pip install .[cli]
```

## Documentation

`apro` commands can be listed with `apro --help`

``` bash
apro --help
                                                                                                                               
 Usage: apro [OPTIONS] COMMAND [ARGS]...                                                                                       
                                                                                                                               
 Main entry point for the CLI.                                                                                                 
                                                                                                                               
                                                                                                                               
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --version             -v        Show the application version and exit                                                       │
│ --install-completion            Install completion for the current shell.                                                   │
│ --show-completion               Show completion for the current shell, to copy it or customize the installation.            │
│ --help                          Show this message and exit.                                                                 │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ run           run aprofiles standard workflow for given dates and specific instruments types                                │
│ climatology   compute climatology from daily AP files                                                                       │
│ l2b           make E-PROFILE L2b files out of AP files                                                                      │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```


### `run` command

``` bash
apro run --help
                                                                                                                               
 Usage: apro run [OPTIONS]                                                                                                     
                                                                                                                               
 run aprofiles standard workflow for given dates and specific instruments types                                                
                                                                                                                               
 see some examples [here](https://augustinmortier.github.io/a-profiles/cli/)                                                   
                                                                                                                               
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --date                                        [%Y-%m-%d]              📅 Processing date.                                   │
│ --from                                        [%Y-%m-%d]              📅 Initial date. [default: None]                      │
│ --to                                          [%Y-%m-%d]              📅 Ending date. [default: (Today's date)]             │
│ --today               --no-today                                      🕑 Process today's data. [default: no-today]          │
│ --yesterday           --no-yesterday                                  🕙 Process yesterday's data. [default: no-yesterday]  │
│ --instruments-type                            [CHM15k|Mini-MPL|CL61]  📗 List of specific instruments to be processed.      │
│                                                                       [default: CHM15k, Mini-MPL]                           │
│ --multiprocessing     --no-multiprocessing                            🚀 Use multiprocessing mode.                          │
│                                                                       [default: no-multiprocessing]                         │
│ --workers                                     INTEGER RANGE [x>=1]    👷 Number of workers (NSLOTS, if multiprocessing mod… │
│                                                                       is enabled).                                          │
│                                                                       [env var: NSLOTS]                                     │
│                                                                       [default: 2]                                          │
│ --path-in                                     PATH                    📂 Base path for input data.                          │
│                                                                       [default: data/e-profile]                             │
│ --path-out                                    PATH                    📂 Base path for output data.                         │
│                                                                       [default: data/v-profiles]                            │
│ --apriori-cfg                                 PATH                    📂 Base path for a priori config file.                │
│                                                                       [default: config]                                     │
│ --update-data         --no-update-data                                📈 Update data. [default: update-data]                │
│ --update-calendar     --no-update-calendar                            🗓️ Update calendar. [default: update-calendar]         │
│ --update-map          --no-update-map                                 🗺️ Update map. [default: update-map]                   │
│ --progress-bar        --no-progress-bar                               ⌛ Show progress bar. [default: progress-bar]         │
│ --help                                                                Show this message and exit.                           │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

#### Examples

##### run a specific date

``` bash
apro run --date 2021-09-09
```

##### run today\'s files

``` bash
apro run --today
```

##### run yesterday\'s files

``` bash
apro run --yesterday
```

It is possible to combine different options.

##### run today\'s and yesterday\'s files for CHM15k only

``` bash
apro run --today --yesterday --instruments-type CHM15k
```

##### update only calendar files for 2021

``` bash
apro run --from 2021-01-01 --to 2021-12-31 --no-update-data --no-update-map
```

##### use multiprocessing

The data processing can be run in parallel by using the
[`multiprocessing`] option :
``` bash
apro run --today --yesterday --multiprocessing
```


### `l2b` command

``` bash
apro l2b --help
                                                                                                                                     
 Usage: apro l2b [OPTIONS]                                                                                                           
                                                                                                                                     
 make E-PROFILE L2b files out of AP files                                                                                            
                                                                                                                                     
╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --path-in                              PATH     📂 Base path for input data. [default: data/v-profiles]                           │
│ --path-out                             PATH     📂 Base path for output data. [default: data/l2b]                                 │
│ --time-steps                           INTEGER  🔂 Number of most recent time steps to be processed. [default: 12]                │
│ --progress-bar    --no-progress-bar             ⌛ Show progress bar. [default: progress-bar]                                     │
│ --help                                          Show this message and exit.                                                       │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### `climatology` command

``` bash
apro climatology --help
                                                                                                                               
 Usage: apro climatology [OPTIONS]                                                                                             
                                                                                                                               
 compute climatology from daily AP files                                                                                       
                                                                                                                               
                                                                                                                               
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --n-days                                     INTEGER               📅 Number of days to be included in the climatology.     │
│                                                                    [default: 90]                                            │
│ --multiprocessing    --no-multiprocessing                          🚀 Use multiprocessing mode.                             │
│                                                                    [default: no-multiprocessing]                            │
│ --workers                                    INTEGER RANGE [x>=1]  👷 Number of workers (NSLOTS, if multiprocessing mode i… │
│                                                                    enabled).                                                │
│                                                                    [env var: NSLOTS]                                        │
│                                                                    [default: 2]                                             │
│ --path-in                                    PATH                  📂 Base path for input data. [default: data/v-profiles]  │
│ --path-out                                   PATH                  📂 Base path for output data. [default: data/v-profiles] │
│ --progress-bar       --no-progress-bar                             ⌛ Show progress bar. [default: progress-bar]            │
│ --help                                                             Show this message and exit.                              │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

#### Examples

##### make L2b files out of today's AP files in default directory

```bash
apro l2b 
```