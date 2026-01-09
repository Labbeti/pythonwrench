#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, Callable, Dict, Generic, Iterable, List, Optional, TypeVar

from typing_extensions import ParamSpec

logger = logging.getLogger(__name__)


P = ParamSpec("P")
T = TypeVar("T")


class ThreadPoolExecutorHelper(Generic[P, T]):
    # Note: use commas for typing because Future is not generic in older python versions

    def __init__(
        self,
        fn: Callable[P, T],
        *,
        executor_kwds: Optional[Dict[str, Any]] = None,
        executor: Optional[ThreadPoolExecutor] = None,
        futures: "Iterable[Future[T]]" = (),
        **default_fn_kwds,
    ) -> None:
        futures = list(futures)

        super().__init__()
        self.fn = fn
        self.executor_kwds = executor_kwds
        self.executor = executor
        self.futures = futures
        self.default_kwargs = default_fn_kwds

    def submit(self, *args: P.args, **kwargs: P.kwargs) -> "Future[T]":
        if self.executor is None:
            executor_kwds = self.executor_kwds
            if executor_kwds is None:
                executor_kwds = {}
            self.executor = ThreadPoolExecutor(**executor_kwds)

        kwargs = self.default_kwargs | kwargs  # type: ignore
        future = self.executor.submit(self.fn, *args, **kwargs)
        self.futures.append(future)
        return future

    def wait_all(self, shutdown: bool = True, verbose: bool = True) -> List[T]:
        futures = self.futures
        if verbose:
            try:
                import tqdm  # type: ignore

                futures = tqdm.tqdm(futures, disable=not verbose)
            except ImportError:
                msg = "Cannot display verbose bar because tqdm is not installed."
                logger.warning(msg)

        results = [future.result() for future in futures]
        self.futures.clear()
        if shutdown and self.executor is not None:
            self.executor.shutdown()
            self.executor = None
        return results
