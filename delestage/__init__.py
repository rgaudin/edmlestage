import datetime
import json
import os
import re
import urllib.parse
from pathlib import Path
from typing import Any, NamedTuple, Self

import requests

API_URL = "https://www.edmsa.ml/ajax/service"
DATA_DIR = Path(os.getenv("DATA_DIR", "DATA"))
GROUPS_PATH = DATA_DIR / "groups.json"
LINES_PATH = DATA_DIR / "lines.json"
DAILY_PATH = DATA_DIR / "DAILY"
USERS_PATH = DATA_DIR / "USERS"
LINES = json.loads(LINES_PATH.read_text())

LOCATION_RE = re.compile(r"^(?P<name>.+)\s\((?P<ident>\d+)\)$")
LINE_RE = re.compile(r"^(?P<name>.+)\s\-\sLIGNE\s\d+$")
NONCE_RE = re.compile(r'"nonce":"(?P<nonce>.+)",')
DATE_FS_FMT = "%Y-%m-%d"
DATE_MSG_FMT = "%A %d %B %Y"
DATE_EDM_FMT = "%Y-%m-%d"
DATE_EDM_REQ_FMT = "%d-%m-%Y"


class Location(NamedTuple):
    name: str
    ident: int

    def __str__(self) -> str:
        return f"{self.name} ({self.ident})"

    @property
    def as_param(self) -> str:
        # return str(self).replace(" ", "+")
        return urllib.parse.quote_plus(str(self))

    @classmethod
    def parse(cls, text: str) -> Self:
        m = LOCATION_RE.match(text)
        if m:
            name = m.groupdict()["name"]
            ident = int(m.groupdict()["ident"])
            return cls(name=name, ident=ident)
        raise ValueError(f"Cannot parse Location for “{text}”")

    @classmethod
    def from_line(cls, line: str) -> Self:
        return cls.parse(LINES[line])  # raises KeyError


def get_std_headers() -> dict[str, str]:
    return {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
    }


def get_nonce() -> str:
    resp = requests.get("https://www.edmsa.ml/programme-delestage", timeout=60)
    resp.raise_for_status()
    for line in resp.text.splitlines():
        if '"nonce":' not in line:
            continue
        m = NONCE_RE.search(line)
        if m:
            return m.groupdict()["nonce"]
    raise ValueError("Unable to find nonce")


def read_json_file(fpath: Path) -> Any:
    return json.loads(fpath.read_text())


def has_data_for(date: datetime.date) -> bool:
    fpaths = [
        DAILY_PATH / date.strftime(DATE_FS_FMT) / f"{group}.json"
        for group in read_json_file(GROUPS_PATH).keys()
    ]
    return all(fpath.exists() for fpath in fpaths)
