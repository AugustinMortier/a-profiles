#!/usr/bin/env python3
# @author Augustin Mortier
# @desc A-Profiles - CLI for running aprofiles standard workflow

import concurrent.futures
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import List

import typer
from pandas import date_range
from rich.progress import Progress, track

import aprofiles.cli.utils as utils

app = typer.Typer(no_args_is_help=True)

class InstrumentType(str, Enum):
    chm15k = "CHM15k"
    minimpl = "Mini-MPL"
    cl61 = "CL61"

@app.command()
def main(
    _dates: List[datetime] = typer.Option(
        [], "--date", formats=["%Y-%m-%d"], help="📅 Processing date."
    ),
    _from: datetime = typer.Option(
        None, "--from", formats=["%Y-%m-%d"], help="📅 Initial date"
    ),
    _to: datetime = typer.Option(
        datetime.today(),
        "--to",
        formats=["%Y-%m-%d"],
        help="📅 Ending date.",
        show_default="Today's date",
    ),
    today: bool = typer.Option(False, help="🕑 Process today."),
    yesterday: bool = typer.Option(False, help="🕙 Process yesterday."),
    instruments_types: List[InstrumentType] = typer.Option(
        ['CHM15k', 'Mini-MPL'], "--instruments-type", help="📗 List of specific instruments to be processed."
    ),
    multiprocessing: bool = typer.Option(False, help="⚡ Use multiprocessing mode."),
    workers: int = typer.Option(
        2, "--workers", min=1, envvar="NSLOTS", help="👷 workers NSLOTS (if multiprocessing mode is enabled)"
    ),
    basedir_in: Path = typer.Option(
        "data/e-profile", exists=True, readable=True, help="📂 Base path for input data."
    ),
    basedir_out: Path = typer.Option(
        "data/v-profiles",
        exists=True,
        writable=True,
        help="📂 Base path for output data.",
    ),
    update_data: bool = typer.Option(True, help="📈 Update data."),
    update_calendar: bool = typer.Option(True, help="🗓️ Update calendar."),
    update_map: bool = typer.Option(True, help="🗺️ Update map."),
    update_climatology: bool = typer.Option(True, help="↪️ Update climatology."),
    progress_bar: bool = typer.Option(True, help="⌛ Progress bar."),
    # rsync: bool = typer.Option(False, help="📤 Rsync to webserver."),
):
    """
    Run aprofiles standard workflow for given dates, optionally for specific instruments types.
    
    See some examples here: https://a-profiles.readthedocs.io/en/latest/cli.html
    """

    #typer.echo(f"dates: {dates}, today: {today}, yesterday: {yesterday}, from: {_from}, to: {_to}, instruments_types: {instruments_types}, multiprocessing: {multiprocessing}")

    #prepare dates array | convert from tuples to list
    dates = list(_dates)
    # today / yesterday
    if today:
        dates.append(datetime.today())
    if yesterday:
        dates.append(datetime.today() - timedelta(days=1))
    # from / to
    if _from is not None:
        for date in date_range(_from, _to, freq="D"):
            dates.append(date)
    # abort if no dates
    if (len(dates) == 0):
        print("No provided date. Please check aprocess --help for more information.")
        raise typer.Abort()

    # progress bar
    if progress_bar:
        disable_progress_bar = False
    else:
        disable_progress_bar = True

    # read config file
    CFG = utils.config.read()

    for date in dates:
        yyyy = str(date.year)
        mm = str(date.month).zfill(2)
        dd = str(date.day).zfill(2)

        # list all files in in directory
        datepath = Path(basedir_in, yyyy, mm, dd)
        onlyfiles = [str(e) for e in datepath.iterdir() if e.is_file()]

        # data processing
        if update_data:
            if multiprocessing:
                with Progress() as progress:
                    task = progress.add_task(f"{date.strftime('%Y-%m-%d')} ⚡", total=len(onlyfiles))
                    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
                        futures = [executor.submit(
                            utils.workflow.workflow, 
                            path=file, 
                            instruments_types=instruments_types, 
                            base_dir=basedir_out, CFG=CFG, verbose=False
                        )
                        for file in onlyfiles]
                        for future in concurrent.futures.as_completed(futures):
                            progress.update(task, advance=1)
            else:
                for file in track(onlyfiles, description=f"{date.strftime('%Y-%m-%d')}   ", disable=disable_progress_bar):
                    utils.workflow.workflow(
                        file, instruments_types, basedir_out, CFG, verbose=False
                    )
        
        # list all files in out directory
        datepath = Path(basedir_out, yyyy, mm, dd)

        if update_calendar:
            # create calendar
            calname = f"{yyyy}-{mm}-cal.json"
            path = Path(basedir_out, yyyy, mm, calname)
            if not path.is_file():
                utils.json_calendar.make_calendar(basedir_out, yyyy, mm, calname)

            # list all files in out directory
            onlyfiles = [str(e) for e in datepath.iterdir() if e.is_file()]
            # add to calendar
            for file in track(onlyfiles, description="calendar     ", disable=disable_progress_bar):
                utils.json_calendar.add_to_calendar(file, basedir_out, yyyy, mm, dd, calname)
            
        
        if update_map:
            # create map
            mapname = f"{yyyy}-{mm}-map.json"
            path = Path(basedir_out, yyyy, mm, mapname)
            if not path.is_file():
                utils.json_map.make_map(basedir_out, yyyy, mm, mapname)

            # list all files in out directory
            onlyfiles = [str(e) for e in datepath.iterdir() if e.is_file()]
            # add to map
            for file in track(onlyfiles, description="map          ", disable=disable_progress_bar):
                utils.json_map.add_to_map(file, basedir_out, yyyy, mm, dd, mapname)

    if update_climatology:
        # list all files in out directory
        onlyfiles = [str(e) for e in datepath.iterdir() if e.is_file()]
        # get station id from file name
        stations_id = ["-".join(onlyfile.split("/")[-1].split("AP_")[1].split("-", 5)[:5]) for onlyfile in onlyfiles]
        # exclude moving stations
        stations_id = [station for station in stations_id if station not in CFG["exclude_stations_id_from_climatology"]]
        
        if multiprocessing:
            with Progress() as progress:
                task = progress.add_task(total=len(stations_id), description=f"clim.      ⚡", disable=disable_progress_bar)
                with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
                    futures = [executor.submit(
                        utils.json_climatology.compute_climatology,
                        basedir_out, 
                        station_id, 
                        variables="extinction", 
                        aerosols_only=True
                    )
                    for station_id in stations_id]
                    for future in concurrent.futures.as_completed(futures):
                        progress.update(task, advance=1)
        else:
            for station_id in track(stations_id, description='clim.        ', disable=disable_progress_bar):
                utils.json_climatology.compute_climatology(basedir_out, station_id, variables="extinction", aerosols_only=True)


if __name__ == "__main__":
    app()
