#!/usr/bin/env python
# -*- coding: utf-8 -*-

from numbers import Real
from typing import Iterable, Optional, TypeVar, Callable, Any

from pythonwrench.functools import function_alias, compose

T = TypeVar("T")
T_Real = TypeVar("T_Real", bound=Real)


def clip(
    x: T_Real,
    xmin: Optional[T_Real] = None,
    xmax: Optional[T_Real] = None,
) -> T_Real:
    if xmin is not None:
        x = max(x, xmin)
    if xmax is not None:
        x = min(x, xmax)
    return x


@function_alias(clip)
def clamp(*args, **kwargs): ...


def argmax(x: Iterable) -> int:
    max_index, _max_value = max(enumerate(x), key=lambda t: t[1])
    return max_index


def argmin(x: Iterable) -> int:
    min_index, _max_value = min(enumerate(x), key=lambda t: t[1])
    return min_index


def argsort(
    x: Iterable[T],
    *,
    key: Optional[Callable[[T], Any]] = None,
    reverse: bool = False,
) -> list[int]:
    def get_second(t: tuple[int, T]) -> T:
        return t[1]

    if key is None:
        key_fn = get_second
    else:
        key_fn = compose(get_second, key)

    sorted_x = sorted(enumerate(x), key=key_fn, reverse=reverse)  # type: ignore
    indices = [idx for idx, _ in sorted_x]
    return indices
