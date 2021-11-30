#!/usr/bin/env python3
# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles - CLI for running aprofiles standard workflow

import concurrent.futures
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

import typer
from pandas import date_range
from tqdm import tqdm

import utils


# def main(dates: List[str], instrument_types: List[str], multithread: bool):
def main(
    date: List[datetime] = typer.Option(
        [], formats=["%Y-%m-%d"], help="📅 Processing date."
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
    instrument_types: List[str] = typer.Option(
        ["CHM15k", "Mini-MPL"], help="📗 List of specific instruments to be processed."
    ),
    multithread: bool = typer.Option(False, help="⚡ Use multithread mode."),
    basedir_in: Path = typer.Option(
        "data/e-profile", exists=True, readable=True, help="📂 Base path for input data."
    ),
    basedir_out: Path = typer.Option(
        "data/v-profiles",
        exists=True,
        writable=True,
        help="📂 Base path for input data.",
    ),
    # rsync: bool = typer.Option(False, help="📤 Rsync to webserver."),
):
    """
    Run aprofiles standard workflow for given dates, optionally for specific instrument types.
    """

    #typer.echo(f"date: {date}, today: {today}, yesterday: {yesterday}, from: {_from}, to: {_to}, instrument_types: {instrument_types}, multithread: {multithread}")

    # makes list of dates
    if len(date) > 0:
        dates = list(date)
    elif today or yesterday:
        dates = []
        if today:
            dates.append(datetime.today())
        if yesterday:
            dates.append(datetime.today() - timedelta(days=1))
    elif _from is not None:
        dates = date_range(_from, _to, freq="D")

    for date in dates:

        yyyy = str(date.year)
        mm = str(date.month).zfill(2)
        dd = str(date.day).zfill(2)

        # list all files in in directory
        datepath = Path(basedir_in) / yyyy / mm / dd
        onlyfiles = [str(e) for e in datepath.iterdir() if e.is_file()]


        # data processing
        if multithread:
            with tqdm(total=len(onlyfiles), desc=date.strftime("%Y-%m-%d")) as pbar:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = [executor.submit(
                        utils.workflow.workflow, 
                        path=file, 
                        instrument_types=instrument_types, 
                        base_dir=basedir_out, verbose=False
                    ) 
                    for file in onlyfiles]
                    for future in concurrent.futures.as_completed(futures):
                        pbar.update(1)
        else:
            for file in tqdm(onlyfiles, desc=date.strftime("%Y-%m-%d")):
                utils.workflow.workflow(
                    file, instrument_types, basedir_out, verbose=False
                )

        # list all files in out directory
        datepath = Path(basedir_out) / yyyy / mm / dd
        onlyfiles = [str(e) for e in datepath.iterdir() if e.is_file()]

        # create calendar
        calname = f"{yyyy}-{mm}-cal.json"
        path = Path(basedir_out) / yyyy / mm / dd / calname
        if not path.exists():
            utils.json_calendar.make_calendar(basedir_out, yyyy, mm, calname)

        # add to calendar
        for file in tqdm(onlyfiles, desc="calendar  "):
            utils.json_calendar.add_to_calendar(file, basedir_out, yyyy, mm, dd, calname)

        # create map
        mapname = f"{yyyy}-{mm}-map.json"
        path = Path(basedir_out) / yyyy / mm / dd / mapname
        if not path.exists():
            utils.json_map.make_map(basedir_out, yyyy, mm, mapname)

        # add to map
        for file in tqdm(onlyfiles, desc="map       "):
            utils.json_map.add_to_map(file, basedir_out, yyyy, mm, dd, mapname)


if __name__ == "__main__":
    typer.run(main)
