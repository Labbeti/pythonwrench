#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections.abc import Iterable as _Iterable
from typing import (
    Any,
    Iterable,
    Literal,
    Union,
    get_origin,
)


def _is_iterable_type_like(x: Any) -> bool:
    return any(xi in (list, Iterable, _Iterable) for xi in (x, get_origin(x)))


def _is_literal(x: Any) -> bool:
    origin = get_origin(x)
    return origin is Literal


def _is_optional(x: Any) -> bool:
    return getattr(x, "__name__", None) == "Optional"


def _is_union(x: Any) -> bool:
    origin = get_origin(x)
    return origin == Union or getattr(origin, "__name__", None) in (
        "Union",
        "UnionType",
    )
