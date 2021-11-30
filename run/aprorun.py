#!/usr/bin/env python3
# @author Augustin Mortier
# @email augustinm@met.no
# @desc A-Profiles - CLI for running aprofiles standard workflow

import concurrent.futures
import os

from tqdm import tqdm

import utils

def _main(dates, instrument_types, multithread):

    for date in dates:
        yyyy = date.split("-")[0]
        mm = date.split("-")[1]
        dd = date.split("-")[2]

        # list all files in in directory
        datepath = os.path.join(BASE_DIR_IN, yyyy, mm, dd)
        onlyfiles = [
            f for f in os.listdir(datepath) if os.path.isfile(os.path.join(datepath, f))
        ]

        # data processing
        if multithread:
            with tqdm(total=len(onlyfiles), desc=date) as pbar:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = [
                        executor.submit(
                            utils.workflow.workflow,
                            path=os.path.join(datepath, filename),
                            instrument_types=instrument_types,
                            base_dir=BASE_DIR_OUT,
                            verbose=False,
                        )
                        for filename in onlyfiles
                    ]
                    for future in concurrent.futures.as_completed(futures):
                        pbar.update(1)
        else:
            for i in tqdm(range(len(onlyfiles)), desc=date):
                path = os.path.join(datepath, onlyfiles[i])
                utils.workflow.workflow(
                    path, instrument_types, BASE_DIR_OUT, verbose=False
                )

        # list all files in out directory
        datepath = os.path.join(BASE_DIR_OUT, yyyy, mm, dd)
        onlyfiles = [
            f for f in os.listdir(datepath) if os.path.isfile(os.path.join(datepath, f))
        ]

        # create calendar
        calname = f"{yyyy}-{mm}-cal.json"
        if not os.path.exists(
            os.path.join(BASE_DIR_OUT, yyyy, mm, "calendar", calname)
        ):
            utils.json_calendar.make_calendar(BASE_DIR_OUT, yyyy, mm, calname)

        # add to calendar
        for i in tqdm(range(len(onlyfiles)), desc="calendar  "):
            fn = os.path.join(BASE_DIR_OUT, yyyy, mm, dd, onlyfiles[i])
            utils.json_calendar.add_to_calendar(fn, BASE_DIR_OUT, yyyy, mm, dd, calname)

        # create map
        mapname = f"{yyyy}-{mm}-map.json"
        if not os.path.exists(os.path.join(BASE_DIR_OUT, yyyy, mm, mapname)):
            utils.json_map.make_map(BASE_DIR_OUT, yyyy, mm, mapname)

        # add to map
        for i in tqdm(range(len(onlyfiles)), desc="map       "):
            fn = os.path.join(BASE_DIR_OUT, yyyy, mm, dd, onlyfiles[i])
            utils.json_map.add_to_map(fn, BASE_DIR_OUT, yyyy, mm, dd, mapname)


if __name__ == "__main__":
    import argparse
    from datetime import datetime, timedelta
    from pandas import date_range

    def _validate_dates(str_date1, str_date2=None):
        try:
            datetime.strptime(str_date1, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Incorrect data format, should be YYYY-MM-DD")

        if str_date2 is not None:
            try:
                datetime.strptime(str_date2, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Incorrect data format, should be YYYY-MM-DD")
            if str_date1 > str_date2:
                raise ValueError(
                    f"from_date ({str_date1}) must be anterior to to_date ({str_date2})"
                )

    # Create the parser
    my_parser = argparse.ArgumentParser(
        prog="aprofiles",
        usage="%(prog)s [options] date",
        description="Run standard A-Profiles workflow",
    )

    # Add arguments
    my_parser.add_argument(
        "-d",
        "--date",
        metavar="date",
        nargs="?",
        type=str,
        help="date to be processed (yyyy-mm-dd)",
    )

    my_parser.add_argument(
        "-t",
        "--today",
        action='store_true',
        help="process today",
    )

    my_parser.add_argument(
        "-y",
        "--yesterday",
        action='store_true',
        help="process yesterday",
    )

    my_parser.add_argument(
        "--from",
        metavar="from",
        dest="_from",
        nargs="?",
        type=str,
        help="Initial date to be processed (yyyy-mm-dd)",
    )

    my_parser.add_argument(
        "--to",
        metavar="to",
        dest="_to",
        nargs="?",
        default=datetime.today().strftime("%Y-%m-%d"),
        type=str,
        help="Last date to be processed (yyyy-mm-dd)",
    )

    my_parser.add_argument(
        "-i",
        "--instruments",
        metavar="instruments",
        nargs="?",
        default=["CHM15k", "mini-MPL"],
        type=str,
        help="Instrument types to be processed",
    )

    my_parser.add_argument(
        "-m",
        "--multithread",
        action='store_true',
        help="Use multithread for data processing",
    )

    # Execute the parse_args() method
    args = my_parser.parse_args()

    #print(f'args: {args}')

    # Prepare dates array
    if args.date is not None:
        _validate_dates(args.date)
        dates = [args.date]
    elif args._from is not None:
        _validate_dates(args._from, args._to)
        dates = [str(date).split('T')[0] for date in date_range(args._from, args._to, freq="D").values]
    else:
        dates = []
        if args.today:
            dates.append(datetime.today().strftime("%Y-%m-%d"))
        if args.yesterday:
            dates.append((datetime.today()-timedelta(days=1)).strftime("%Y-%m-%d"))

    # data path
    BASE_DIR_IN = "data/e-profile"
    BASE_DIR_OUT = "data/v-profiles"

    _main(dates, instrument_types=args.instruments, multithread=args.multithread)
