#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import shutil
import time
from functools import wraps
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Literal,
    Optional,
    Tuple,
    TypedDict,
    TypeVar,
    Union,
    get_args,
)

from typing_extensions import ParamSpec

from pythonwrench.checksum import checksum_any
from pythonwrench.datetime import get_now
from pythonwrench.inspect import get_fullname

T = TypeVar("T")
P = ParamSpec("P")
U = TypeVar("U")


ChecksumFn = Callable[[Tuple[Callable[P, T], Tuple, Dict[str, Any]]], int]
SavingBackend = Literal["csv", "json", "pickle"]
StoreMode = Literal["outputs_only", "outputs_metadata", "outputs_metadata_inputs"]


class CacheMeta(TypedDict):
    datetime: str
    duration: float
    checksum: int
    fn_name: str
    output: Any
    input: Optional[Tuple[Any, Any]]


DEFAULT_CACHE_DPATH = Path.home().joinpath(".cache", "disk_cache")


logger = logging.getLogger(__name__)


def disk_cache_call(
    fn: Callable[..., T],
    *args,
    cache_dpath: Union[str, Path, None] = None,
    cache_force: bool = False,
    cache_verbose: int = 0,
    cache_checksum_fn: ChecksumFn = checksum_any,
    cache_saving_backend: Optional[SavingBackend] = "pickle",
    cache_fname_fmt: Optional[str] = None,
    cache_dump_fn: Optional[Callable[[Any, Path], Any]] = None,
    cache_load_fn: Optional[Callable[[Path], Any]] = None,
    cache_enable: bool = True,
    cache_store_mode: StoreMode = "outputs_metadata",
    **kwargs,
) -> T:
    """Call function and store output in a cache file.

    Cache file is identified by the checksum of the function arguments, and stored by default in `~/.cache/disk_cache/<Function_name>/` directory.

    ```python
    >>> import pythonwrench as pw
    >>> def heavy_processing():
    >>>     # Lot of stuff here
    >>>     ...
    >>> outputs = pw.disk_cache_call(heavy_processing)  # first time function is called
    >>> outputs = pw.disk_cache_call(heavy_processing)  # second time outputs is loaded from disk
    ```
    """
    wrapped_fn = disk_cache_decorator(
        fn,
        cache_dpath=cache_dpath,
        cache_force=cache_force,
        cache_verbose=cache_verbose,
        cache_checksum_fn=cache_checksum_fn,
        cache_saving_backend=cache_saving_backend,
        cache_fname_fmt=cache_fname_fmt,
        cache_dump_fn=cache_dump_fn,
        cache_load_fn=cache_load_fn,
        cache_enable=cache_enable,
        cache_store_mode=cache_store_mode,
    )
    return wrapped_fn(*args, **kwargs)


def disk_cache_decorator(
    fn: Optional[Callable[P, T]] = None,
    *,
    cache_dpath: Union[str, Path, None] = None,
    cache_force: bool = False,
    cache_verbose: int = 0,
    cache_checksum_fn: ChecksumFn = checksum_any,
    cache_saving_backend: Optional[SavingBackend] = "pickle",
    cache_fname_fmt: Optional[str] = None,
    cache_dump_fn: Optional[Callable[[Any, Path], Any]] = None,
    cache_load_fn: Optional[Callable[[Path], Any]] = None,
    cache_enable: bool = True,
    cache_store_mode: StoreMode = "outputs_metadata",
) -> Callable:
    """Decorator to store function output in a cache file.

    Cache file is identified by the checksum of the function arguments, and stored by default in `~/.cache/disk_cache/<Function_name>/` directory.

    ```python
    >>> import pythonwrench as pw
    >>> @pw.disk_cache_decorator
    >>> def heavy_processing():
    >>>     # Lot of stuff here
    >>>     ...
    >>> outputs = heavy_processing()  # first time function is called
    >>> outputs = heavy_processing()  # second time outputs is loaded from disk
    ```
    """
    impl_fn = _disk_cache_impl(
        cache_dpath=cache_dpath,
        cache_force=cache_force,
        cache_verbose=cache_verbose,
        cache_checksum_fn=cache_checksum_fn,
        cache_saving_backend=cache_saving_backend,
        cache_fname_fmt=cache_fname_fmt,
        cache_dump_fn=cache_dump_fn,
        cache_load_fn=cache_load_fn,
        cache_enable=cache_enable,
        cache_store_mode=cache_store_mode,
    )
    if fn is not None:
        return impl_fn(fn)
    else:
        return impl_fn


def _disk_cache_impl(
    *,
    cache_dpath: Union[str, Path, None] = None,
    cache_force: bool = False,
    cache_verbose: int = 0,
    cache_checksum_fn: ChecksumFn = checksum_any,
    cache_saving_backend: Optional[SavingBackend] = "pickle",
    cache_fname_fmt: Optional[str] = None,
    cache_dump_fn: Optional[Callable[[Any, Path], Any]] = None,
    cache_load_fn: Optional[Callable[[Path], Any]] = None,
    cache_enable: bool = True,
    cache_store_mode: StoreMode = "outputs_metadata",
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    if cache_saving_backend == "pickle":
        from pythonwrench.pickle import dump_pickle, load_pickle

        cache_fname_fmt = "{fn_name}_{csum}.pickle"
        cache_dump_fn = dump_pickle
        cache_load_fn = load_pickle

    elif cache_saving_backend == "json":
        from pythonwrench.json import dump_json, load_json

        cache_fname_fmt = "{fn_name}_{csum}.json"
        cache_dump_fn = dump_json
        cache_load_fn = load_json

    elif cache_saving_backend == "csv":
        from pythonwrench.csv import dump_csv, load_csv

        if cache_store_mode != "outputs_only":
            msg = f"Invalid combinaison of arguments {cache_saving_backend=} with {cache_store_mode=}."
            raise ValueError(msg)

        cache_fname_fmt = "{fn_name}_{csum}.csv"
        cache_dump_fn = dump_csv
        cache_load_fn = load_csv

    elif cache_saving_backend is None:
        if cache_fname_fmt is None or cache_dump_fn is None or cache_load_fn is None:
            msg = f"If {cache_saving_backend=}, arguments cache_fname_fmt, cache_dump_fn and cache_load_fn cannot be None. (found {cache_fname_fmt=}, {cache_dump_fn=} {cache_load_fn=})"
            raise ValueError(msg)
    else:
        msg = f"Invalid argument {cache_saving_backend=}. (expected one of {get_args(SavingBackend)})"
        raise ValueError(msg)

    def _disk_cache_impl_fn(fn: Callable[P, T]) -> Callable[P, T]:
        fn_name = get_fullname(fn).replace("<locals>", "_locals_")
        cache_fn_dpath = _get_fn_cache_dpath(fn, cache_dpath=cache_dpath)

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
        def _disk_cache_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            checksum_args = fn, args, kwargs
            csum = cache_checksum_fn(checksum_args)
            cache_fname = cache_fname_fmt.format(fn_name=fn_name, csum=csum)
            cache_fpath = cache_fn_dpath.joinpath(cache_fname)

            if not cache_enable:
                output = fn(*args, **kwargs)

            elif cache_force or not cache_fpath.exists():
                if cache_verbose > 0:
                    logger.info(compute_start_msg.format(now=get_now()))

                start = time.perf_counter()
                output = fn(*args, **kwargs)
                duration = time.perf_counter() - start

                if cache_verbose > 0:
                    logger.info(
                        compute_end_msg.format(now=get_now(), duration=duration)
                    )

                if cache_store_mode == "outputs_only":
                    cache_content = output

                elif (
                    cache_store_mode == "outputs_metadata"
                    or cache_store_mode == "outputs_metadata_inputs"
                ):
                    cache_content = {
                        "datetime": get_now(),
                        "duration": duration,
                        "checksum": csum,
                        "fn_name": fn_name,
                        "output": output,
                        "input": (args, kwargs)
                        if cache_store_mode == "outputs_metadata_inputs"
                        else None,
                    }
                else:
                    msg = f"Invalid argument {cache_store_mode=}. (expected one of {get_args(StoreMode)})"
                    raise ValueError(msg)

                cache_fn_dpath.mkdir(parents=True, exist_ok=True)
                cache_dump_fn(cache_content, cache_fpath)  # type: ignore

            elif cache_fpath.is_file():
                if cache_verbose > 0:
                    logger.info(load_start_msg)

                cache_content: Any = cache_load_fn(cache_fpath)

                if cache_store_mode == "outputs_only":
                    output = cache_content

                elif cache_store_mode == "outputs_metadata":
                    output = cache_content["output"]

                elif cache_store_mode == "outputs_metadata_inputs":
                    output = cache_content["output"]
                    input_ = cache_content["input"]
                    if input_ is not None and input_ != (args, kwargs):
                        os.remove(cache_fpath)
                        return _disk_cache_wrapper(*args, **kwargs)
                else:
                    msg = f"Invalid argument {cache_store_mode=}. (expected one of {get_args(StoreMode)})"
                    raise ValueError(msg)

                if cache_verbose > 0:
                    logger.info(load_end_msg)

                if cache_store_mode != "outputs_only" and cache_verbose > 1:
                    metadata = {k: v for k, v in cache_content.items() if k != "output"}
                    msgs = f"Found cache metadata:\n{metadata}".split("\n")
                    for msg in msgs:
                        logger.debug(msg)

            else:
                msg = f"Path {str(cache_fpath)} exists but it is not a file."
                raise RuntimeError(msg)

            return output

        _disk_cache_wrapper.fn = fn  # type: ignore
        return _disk_cache_wrapper

    return _disk_cache_impl_fn


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
