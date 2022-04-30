# -*- coding: utf-8 -*-
"""
    Common utilities to be used in application
"""

import datetime
import pathlib

# Instance folder path, to keep stuff aware from flask app.
INSTANCE_FOLDER_PATH = pathlib.Path(
    pathlib.Path(__file__).parents[2], "app_data", "app_instance"
)
INSTANCE_FOLDER_PATH.mkdir(exist_ok=True, parents=True)

# Form validation

NAME_LEN_MIN = 4
NAME_LEN_MAX = 25

PASSWORD_LEN_MIN = 6
PASSWORD_LEN_MAX = 16


# Model
STRING_LEN = 64


def get_current_time() -> datetime.datetime:
    return datetime.datetime.utcnow()


def add_offset_days_on_datetime(
    dt: datetime.datetime, num_days: int
) -> datetime.datetime:
    return dt + datetime.timedelta(days=num_days)


def get_current_time_with_offset_days(num_days: int) -> datetime.datetime:
    return datetime.datetime.utcnow() + datetime.timedelta(days=num_days)


def pretty_date(dt, default=None):
    # Returns string representing "time since" eg 3 days ago, 5 hours ago etc.

    if default is None:
        default = "just now"

    now = datetime.datetime.utcnow()
    diff = now - dt

    periods = (
        (diff.days / 365, "year", "years"),
        (diff.days / 30, "month", "months"),
        (diff.days / 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds / 3600, "hour", "hours"),
        (diff.seconds / 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )

    for period, singular, plural in periods:

        if not period:
            continue

        if int(period) >= 1:
            if int(period) > 1:
                return "%d %s ago" % (period, plural)
            return "%d %s ago" % (period, singular)

    return default
