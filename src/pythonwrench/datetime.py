#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

ISO8601_DAY_FORMAT = r"%Y-%m-%d"
ISO8601_HOUR_FORMAT_DOUBLE_DOT = r"%Y-%m-%dT%H:%M:%S"


def get_now_iso8601() -> str:
    """Returns current datetime as string with the ISO8601 format."""
    return get_now(ISO8601_HOUR_FORMAT_DOUBLE_DOT)


def get_now(fmt: str = ISO8601_HOUR_FORMAT_DOUBLE_DOT) -> str:
    """Returns current datetime as string with the specified format."""
    return datetime.datetime.now().strftime(fmt)
