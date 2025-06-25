#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import MISSING
from typing import Any, Dict

from pythonwrench.typing.checks import is_dataclass_instance  # noqa: F401
from pythonwrench.typing.classes import DataclassInstance


def get_defaults_values(obj: DataclassInstance) -> Dict[str, Any]:
    defaults = {}

    for field in obj.__dataclass_fields__.values():
        if callable(field.default_factory):
            default = field.default_factory()
        else:
            default = field.default

        if default != MISSING:
            defaults[field.name] = default

    return defaults
