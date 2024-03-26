import datetime
import os
from collections.abc import Callable

import yagmail
from babel.dates import format_date

from delestage import (
    DAILY_PATH,
    DATE_FS_FMT,
    GROUPS_PATH,
    USERS_PATH,
    read_json_file,
)


def send_to_void(ident: str, message: str): ...


def send_via_gmail(ident: str, subject: str, message: str):
    username = os.getenv("GMAIL_USERNAME", "-")
    yag = yagmail.SMTP(username, os.getenv("GMAIL_PASSWORD", "-"))
    yag.send(
        headers={"From": "Délestages EDM"},
        to=ident,
        subject=subject,
        contents=message,
    )


def get_user_target(name: str) -> tuple[Callable, str]:
    if name.startswith("email_"):
        return send_via_gmail, name.rsplit("email_", 1)[1]
    return send_to_void, "-"


def fmt(hour: int) -> str:
    """repr of an hour in text"""
    return str(hour).zfill(2)


def get_hours_text(hours: list[int]) -> str:
    """Text as “De 4h à 12h puis de 22h à 23h” from list of hours ints"""
    text = ""
    nb_hours = 0
    started = False
    hours.sort()  # make sure we're progressing together
    for hour in range(0, 24):  # EDM numbers are from 0 to 23
        if hour in hours and not started:  # start of cut
            started = True
            if nb_hours > 0:
                text += " puis"
            text += f" de {fmt(hour)}h"
            continue
        elif hour not in hours and started:  # end of cut
            text += f" à {fmt(hour)}h"
            started = False
            nb_hours += 1

    if started:
        text += " à minuit"

    text = text.strip()
    text = text[0].upper() + text[1:]
    text += "."

    return text


def build_message_for(all_data: dict, user_req: dict) -> str | None:
    if not user_req.get("groups"):
        return
    messages = []
    for group in user_req["groups"]:
        if not group.get("name"):
            continue
        label = group.get("label", group["name"])
        data = all_data[group["name"]]
        nb_hours = len(data["hours"])
        hours_text = get_hours_text(data["hours"])
        messages.append(f"- {label}: {hours_text} ({nb_hours}h)")

    return "\n".join(messages) if messages else None


def send_data_for(date: datetime.date):
    # read all groups data first
    groups_data = {}
    for group in read_json_file(GROUPS_PATH).keys():
        fpath = DAILY_PATH / date.strftime(DATE_FS_FMT) / f"{group}.json"
        groups_data[group] = read_json_file(fpath)

    # loop over users to send them custom messages
    USERS_PATH.mkdir(parents=True, exist_ok=True)
    for user_fpath in USERS_PATH.glob("*.json"):
        func, ident = get_user_target(user_fpath.stem)
        message = build_message_for(
            all_data=groups_data, user_req=read_json_file(user_fpath)
        )
        subject = (
            f"Heures de fournitures pour "
            f"{format_date(date, format='full', locale='fr_FR')}"
        )
        print(message)
        if message:
            func(ident=ident, subject=subject, message=message)


def send_data_for_multi(dates: list[datetime.date]):
    if len(dates) == 1:
        return send_data_for(dates[0])

    # read all groups data first
    days_data = {}
    for date in dates:
        days_data[date] = {}
        for group in read_json_file(GROUPS_PATH).keys():
            fpath = DAILY_PATH / date.strftime(DATE_FS_FMT) / f"{group}.json"
            days_data[date][group] = read_json_file(fpath)

    # loop over users to send them custom messages
    USERS_PATH.mkdir(parents=True, exist_ok=True)
    for user_fpath in USERS_PATH.glob("*.json"):
        func, ident = get_user_target(user_fpath.stem)
        intro = "Heures de fournitures d'électricité :"
        outro = (
            "D'après les données d'EDM S.A "
            "via https://www.edmsa.ml/programme-delestage"
        )

        message = str(intro) + "\n\n"

        for date in dates:
            message += format_date(date, format="full", locale="fr_FR").upper() + "\n"

            message += build_message_for(
                all_data=days_data[date], user_req=read_json_file(user_fpath)
            )
            message += "\n\n"

        message += str(outro)

        subject = (
            f"Heures de fournitures "
            f"du {format_date(dates[0], format='short', locale='fr_FR')} "
            f"au {format_date(dates[-1], format='short', locale='fr_FR')}"
        )
        print(message)
        if message:
            func(ident=ident, subject=subject, message=message)


if __name__ == "__main__":
    today = datetime.datetime.now(tz=datetime.UTC).date()
    tomorrow = today + datetime.timedelta(days=1)
    da_tomorrow = tomorrow + datetime.timedelta(days=1)
    send_data_for_multi([tomorrow, da_tomorrow])
