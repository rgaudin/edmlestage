import datetime
import json
import random

import requests

from delestage import (
    API_URL,
    DAILY_PATH,
    DATE_EDM_FMT,
    DATE_EDM_REQ_FMT,
    DATE_FS_FMT,
    GROUPS_PATH,
    Location,
    get_nonce,
    get_std_headers,
    has_data_for,
)


def get_data_for(date: datetime.date) -> int:
    if has_data_for(date):
        return -1
    nonce = get_nonce()
    groups = json.loads(GROUPS_PATH.read_text())
    for group, lines in groups.items():
        print(group)  # noqa: T201
        line = random.choice(lines)  # noqa: S311
        location = Location.from_line(line)
        print(">", line)  # noqa: T201
        resp = requests.post(
            API_URL,
            headers=get_std_headers(),
            data={
                "i": location.as_param,
                "nc": nonce,
                "a": 22,
                "v": date.strftime(DATE_EDM_REQ_FMT),
            },
            timeout=60,
        )
        resp.raise_for_status()
        try:
            entries = resp.json()
        except Exception as exc:
            raise exc

        if not entries:
            print(f"No Data for {date}")  # noqa: T201
            return 1

        for entry in entries:
            # dont send requests if server hasn't updated yet
            if entry["datedebut"] != date.strftime(DATE_EDM_FMT):
                print(  # noqa: T201
                    f"Data for {date} not available: {entry['datedebut']}"
                )
                return 1

            if entry["departquartier_line"] != line:
                continue

            hours = [int(hour) for hour in entry["horaire"].split(",")]
            print(group, len(hours), "hours")  # noqa: T201
            fpath = DAILY_PATH / date.strftime(DATE_FS_FMT) / f"{group}.json"
            fpath.parent.mkdir(parents=True, exist_ok=True)
            fpath.write_text(json.dumps({"hours": hours, "source": entry}, indent=2))
            break
    return 0


if __name__ == "__main__":
    today = datetime.datetime.now(tz=datetime.UTC).date()
    tomorrow = today + datetime.timedelta(days=1)
    da_tomorrow = tomorrow + datetime.timedelta(days=1)
    da2_tomorrow = da_tomorrow + datetime.timedelta(days=1)
    # get_data_for(today)
    get_data_for(da_tomorrow)
