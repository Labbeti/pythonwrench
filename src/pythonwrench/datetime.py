#!/usr/bin/env python

import datetime
from typing import Optional

ISO8601_DAY_FORMAT = r"%Y-%m-%d"
ISO8601_HOUR_FORMAT_DOUBLE_DOT = r"%Y-%m-%dT%H:%M:%S"


def get_now_iso8601(tz: Optional[datetime.timezone] = None) -> str:
    """Returns current datetime as string with the ISO8601 format."""
    return get_now(ISO8601_HOUR_FORMAT_DOUBLE_DOT, tz)


def get_now(
    fmt: str = ISO8601_HOUR_FORMAT_DOUBLE_DOT, tz: Optional[datetime.timezone] = None
) -> str:
    """Returns current datetime as string with the specified format."""
    return datetime.datetime.now(tz).strftime(fmt)
