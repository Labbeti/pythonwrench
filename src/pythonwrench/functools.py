#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import pickle
import shutil
import time
from functools import wraps
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Optional,
    Tuple,
    TypedDict,
    TypeVar,
    Union,
    overload,
)

from typing_extensions import ParamSpec

from pythonwrench._core import _decorator_factory, return_none  # noqa: F401
from pythonwrench.checksum import checksum_any
from pythonwrench.datetime import get_now
from pythonwrench.inspect import get_argnames, get_fullname
from pythonwrench.json import dump_json

T = TypeVar("T")
P = ParamSpec("P")

ChecksumFn = Callable[[Tuple[Callable[P, T], Tuple, Dict[str, Any]]], int]


class CacheContent(TypedDict):
    datetime: str
    duration: float
    checksum: int
    fn_name: str
    output: Any
    input: Optional[tuple[Any, Any]]


DEFAULT_CACHE_DPATH = Path.home().joinpath(".cache", "disk_cache")

pylog = logging.getLogger(__name__)


P = ParamSpec("P")
T = TypeVar("T")
U = TypeVar("U")


def identity(x: T) -> T:
    """Identity function placeholder."""
    return x


def function_alias(alternative: Callable[P, U]) -> Callable[..., Callable[P, U]]:
    return _decorator_factory(alternative)


class Compose(Generic[T, U]):
    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(
        self,
        fn0: Callable[[T], U],
        /,
    ) -> None: ...

    @overload
    def __init__(
        self,
        fn0: Callable[[T], Any],
        fn1: Callable[[Any], U],
        /,
    ) -> None: ...

    @overload
    def __init__(
        self,
        fn0: Callable[[T], Any],
        fn1: Callable[[Any], Any],
        fn2: Callable[[Any], U],
        /,
    ) -> None: ...

    @overload
    def __init__(
        self,
        fn0: Callable[[T], Any],
        fn1: Callable[[Any], Any],
        fn2: Callable[[Any], Any],
        fn3: Callable[[Any], U],
        /,
    ) -> None: ...

    @overload
    def __init__(
        self,
        fn0: Callable[[T], Any],
        fn1: Callable[[Any], Any],
        fn2: Callable[[Any], Any],
        fn3: Callable[[Any], Any],
        fn4: Callable[[Any], U],
        /,
    ) -> None: ...

    @overload
    def __init__(self, *fns: Callable) -> None: ...

    def __init__(self, *fns: Callable) -> None:
        super().__init__()
        self.fns = fns

    def __call__(self, x: T) -> U:
        for fn in self.fns:
            x = fn(x)
        return x  # type: ignore

    def __getitem__(self, idx: int, /) -> Callable[[Any], Any]:
        return self.fns[idx]

    def __len__(self) -> int:
        return len(self.fns)


compose = Compose  # type: ignore


def filter_and_call(fn: Callable[..., T], **kwargs: Any) -> T:
    """Filter kwargs with function arg names and call function."""
    argnames = get_argnames(fn)
    kwargs_filtered = {
        name: value for name, value in kwargs.items() if name in argnames
    }
    return fn(**kwargs_filtered)


def disk_cache_decorator(
    fn: Callable[P, T],
    *,
    cache_dpath: Union[str, Path, None] = None,
    cache_force: bool = False,
    cache_verbose: int = 0,
    cache_checksum_fn: ChecksumFn = checksum_any,
    cache_fname_fmt: str = "{fn_name}_{csum}.pickle",
    cache_dumps_fn: Callable[[CacheContent], bytes] = pickle.dumps,
    cache_loads_fn: Callable[[bytes], CacheContent] = pickle.loads,
    cache_enable: bool = True,
    cache_store_args: bool = False,
) -> Callable[P, T]:
    """Decorator to store function output in a cache file.

    Cache file is identified by the checksum of the function arguments, and stored by default in `~/.cache/disk_cache/<Function_name>/` directory.
    """
    fn_name = get_fullname(fn).replace("<locals>", "_locals_")
    cache_fn_dpath = _get_fn_cache_dpath(fn, cache_dpath=cache_dpath)
    del cache_dpath

    if cache_force:
        compute_start_msg = f"[{fn_name}] Force mode enabled, computing outputs'... (started at {{now}})"
    else:
        compute_start_msg = (
            f"[{fn_name}] Cache missed, computing outputs... (started at {{now}})"
        )
    compute_end_msg = (
        f"[{fn_name}] Outputs computed in {{duration:.1f}}s. (ended at {{now}})"
    )
    load_start_msg = f"[{fn_name}] Loading cache..."
    load_end_msg = f"[{fn_name}] Cache loaded."

    @wraps(fn)
    def disk_cache_impl(*args: P.args, **kwargs: P.kwargs) -> T:
        checksum_args = fn, args, kwargs
        csum = cache_checksum_fn(checksum_args)
        cache_fname = cache_fname_fmt.format(fn_name=fn_name, csum=csum)
        cache_fpath = cache_fn_dpath.joinpath(cache_fname)

        if not cache_enable:
            output = fn(*args, **kwargs)

        elif cache_force or not cache_fpath.exists():
            if cache_verbose > 0:
                pylog.info(compute_start_msg.format(now=get_now()))

            start = time.perf_counter()
            output = fn(*args, **kwargs)
            duration = time.perf_counter() - start

            if cache_verbose > 0:
                pylog.info(compute_end_msg.format(now=get_now(), duration=duration))

            cache_content: CacheContent = {
                "datetime": get_now(),
                "duration": duration,
                "checksum": csum,
                "fn_name": fn_name,
                "output": output,
                "input": (args, kwargs) if cache_store_args else None,
            }
            cache_bytes = cache_dumps_fn(cache_content)

            cache_fn_dpath.mkdir(parents=True, exist_ok=True)
            cache_fpath.write_bytes(cache_bytes)

        elif cache_fpath.is_file():
            if cache_verbose > 0:
                pylog.info(load_start_msg)

            cache_bytes = cache_fpath.read_bytes()
            cache_content = cache_loads_fn(cache_bytes)

            input_ = cache_content["input"]
            if cache_store_args and input_ is not None and input_ != (args, kwargs):
                os.remove(cache_fpath)
                return disk_cache_impl(*args, **kwargs)

            output = cache_content["output"]

            if cache_verbose > 0:
                pylog.info(load_end_msg)

            if cache_verbose > 1:
                metadata = {k: v for k, v in cache_content.items() if k != "output"}
                msgs = f"Found cache metadata:\n{dump_json(metadata)}".split("\n")
                for msg in msgs:
                    pylog.debug(msg)

        else:
            raise RuntimeError(f"Path {str(cache_fpath)} exists but it is not a file.")

        return output

    disk_cache_impl.fn = fn  # type: ignore
    return disk_cache_impl


def disk_cache_call(
    fn: Callable[..., T],
    *args,
    cache_dpath: Union[str, Path, None] = None,
    cache_force: bool = False,
    cache_verbose: int = 0,
    cache_checksum_fn: ChecksumFn = checksum_any,
    cache_fname_fmt: str = "{fn_name}_{csum}.pickle",
    cache_dumps_fn: Callable[[CacheContent], bytes] = pickle.dumps,
    cache_loads_fn: Callable[[bytes], CacheContent] = pickle.loads,
    cache_enable: bool = True,
    cache_store_args: bool = False,
    **kwargs,
) -> T:
    wrapped_fn = disk_cache_decorator(
        fn,
        cache_dpath=cache_dpath,
        cache_force=cache_force,
        cache_verbose=cache_verbose,
        cache_checksum_fn=cache_checksum_fn,
        cache_fname_fmt=cache_fname_fmt,
        cache_dumps_fn=cache_dumps_fn,
        cache_loads_fn=cache_loads_fn,
        cache_enable=cache_enable,
        cache_store_args=cache_store_args,
    )
    return wrapped_fn(*args, **kwargs)


def get_cache_dpath(cache_dpath: Union[str, Path, None] = None) -> Path:
    if cache_dpath is None:
        cache_dpath = DEFAULT_CACHE_DPATH
    else:
        cache_dpath = Path(cache_dpath)
    return cache_dpath


def remove_fn_cache(
    fn: Callable,
    *,
    cache_dpath: Union[str, Path, None] = None,
) -> None:
    cache_fn_dpath = _get_fn_cache_dpath(fn, cache_dpath=cache_dpath)
    if cache_fn_dpath.is_dir():
        shutil.rmtree(cache_fn_dpath)


def _get_fn_cache_dpath(
    fn: Callable,
    *,
    cache_dpath: Union[str, Path, None] = None,
) -> Path:
    fn_name = get_fullname(fn).replace("<locals>", "_locals_")
    cache_dpath = get_cache_dpath(cache_dpath)
    cache_fn_dpath = cache_dpath.joinpath(fn_name)
    return cache_fn_dpath
