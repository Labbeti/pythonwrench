#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import string

from typing import Iterable


def randstr(size: int = 10, letters: Iterable[str] = string.ascii_letters) -> str:
    """Returns a randomly generated string."""
    letters = list(letters)
    return "".join(random.choice(letters) for _ in range(size))
