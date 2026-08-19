#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from typing import Callable, Optional

from typing_extensions import Self


class Ticker:
    def __init__(
        self,
        *,
        get_time_fn: Callable[[], float] = time.perf_counter,
        prev_tick: Optional[float] = None,
    ) -> None:
        """Utility class to show time elapsed since last tick."""
        if prev_tick is None:
            prev_tick = get_time_fn()

        super().__init__()
        self._get_time_fn = get_time_fn
        self._prev_tick = prev_tick

    def tick(self) -> float:
        """Set tick time and returns duration since last tick."""
        now = self._get_time_fn()
        duration = now - self._prev_tick
        self._prev_tick = now
        return duration

    def set_prev_tick(self, prev_tick: Optional[float] = None) -> None:
        """Set tick time."""
        if prev_tick is None:
            prev_tick = self._get_time_fn()
        self._prev_tick = prev_tick

    def get_elapsed_duration(self) -> float:
        """Returns elapsed time since last tick. If no tick has been set, returns 0."""
        if self._prev_tick is None:
            return 0.0
        now = self._get_time_fn()
        duration = now - self._prev_tick
        return duration

    def __enter__(self) -> Self:
        self.tick()
        return self

    def __exit__(self, exc_type, exc, tb):
        pass
