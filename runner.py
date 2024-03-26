#!/usr/bin/env python

import datetime
import time

from delestage import (
    GROUPS_PATH,
    LINES_PATH,
)
from delestage.get import get_data_for
from delestage.groups import retrieve_groups
from delestage.send import send_data_for_multi


def fetch() -> list[datetime.date]:
    # start yesterday so we can incr safely
    date = datetime.datetime.now(tz=datetime.UTC).date() - datetime.timedelta(days=1)
    dates_fetched = []

    while True:
        date = date + datetime.timedelta(days=1)
        rc = get_data_for(date)
        if rc == -1:
            continue
        elif rc == 1:
            # not avail, we're fone
            return dates_fetched
        elif rc == 0:
            dates_fetched.append(date)


def main():
    if not GROUPS_PATH.exists() or not LINES_PATH.exists():
        retrieve_groups()

    while True:
        fetched_dates = fetch()
        if fetched_dates:
            print(f"Found {fetched_dates}")
            send_data_for_multi(fetched_dates)
        print("time to sleep")
        time.sleep(15 * 60)


if __name__ == "__main__":
    main()
