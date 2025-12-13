#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Callable, Generic, List, Optional, TypeVar

from typing_extensions import ParamSpec

logger = logging.getLogger(__name__)


P = ParamSpec("P")
T = TypeVar("T")


class ThreadPoolExecutorHelper(Generic[P, T]):
    def __init__(self, fn: Callable[P, T], **default_kwargs) -> None:
        super().__init__()
        self.fn = fn
        self.default_kwargs = default_kwargs
        self.executor: Optional[ThreadPoolExecutor] = None
        self.futures: list[Future[T]] = []

    def submit(self, *args: P.args, **kwargs: P.kwargs) -> Future[T]:
        if self.executor is None:
            self.executor = ThreadPoolExecutor()

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
                logger.warning(
                    "Cannot display verbose bar because tqdm is not installed."
                )

        results = [future.result() for future in futures]
        self.futures.clear()
        if shutdown and self.executor is not None:
            self.executor.shutdown()
            self.executor = None
        return results
