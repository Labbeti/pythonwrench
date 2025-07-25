#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
from difflib import SequenceMatcher
from typing import Callable, Iterable, Optional


def sequence_matcher_ratio(a: str, b: str) -> float:
    """Compute distance ratio of two strings."""
    return SequenceMatcher(None, a, b).ratio()


def find_closest_in_list(
    x: str,
    lst: Iterable[str],
    sim_fn: Callable[[str, str], float] = sequence_matcher_ratio,
    higher_is_closer: bool = True,
) -> Optional[str]:
    """Find closest element in a list based on matches ratio."""
    best_sim = -int(higher_is_closer) * math.inf
    closest = None

    for elt in lst:
        sim = sim_fn(x, elt)
        if (higher_is_closer and best_sim < sim) or (
            not higher_is_closer and best_sim > sim
        ):
            best_sim = sim
            closest = elt

    if math.isinf(best_sim):
        msg = f"Invalid argument {lst=}. (expected non-empty iterable of strings)"
        raise ValueError(msg)

    return closest
