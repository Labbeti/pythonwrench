#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import string
from typing import Iterable, Optional, overload


@overload
def randstr(
    size: int = 10,
    high: None = None,
    /,
    *,
    letters: Iterable[str] = string.ascii_letters,
) -> str: ...


@overload
def randstr(
    low: int,
    high: int,
    /,
    *,
    letters: Iterable[str] = string.ascii_letters,
) -> str: ...


def randstr(
    low_or_size: int = 10,
    high: Optional[int] = None,
    /,
    *,
    letters: Iterable[str] = string.ascii_letters,
) -> str:
    """Returns a randomly generated string."""
    assert low_or_size >= 0
    if high is None:
        size = low_or_size
    else:
        assert low_or_size < high
        size = random.randint(low_or_size, high - 1)

    letters = list(letters)
    return "".join(random.choice(letters) for _ in range(size))
