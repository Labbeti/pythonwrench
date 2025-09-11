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
    seed: Optional[int] = None,
) -> str: ...


@overload
def randstr(
    low: int,
    high: int,
    /,
    *,
    letters: Iterable[str] = string.ascii_letters,
    seed: Optional[int] = None,
) -> str: ...


def randstr(
    low_or_size: int = 10,
    high: Optional[int] = None,
    /,
    *,
    letters: Iterable[str] = string.ascii_letters,
    seed: Optional[int] = None,
) -> str:
    """Returns a randomly generated string of a random range length."""
    assert low_or_size >= 0

    initial_state = random.getstate()
    if high is None:
        size = low_or_size
        random.seed(seed)
    else:
        assert low_or_size < high
        random.seed(seed)
        size = random.randint(low_or_size, high - 1)

    letters = list(letters)
    result = "".join(random.choice(letters) for _ in range(size))

    if seed is not None:
        random.setstate(initial_state)
    return result
