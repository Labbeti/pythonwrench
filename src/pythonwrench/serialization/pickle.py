#!/usr/bin/env python

import os
import pickle
from os import PathLike
from pathlib import Path
from pickle import UnpicklingError
from typing import Any, BinaryIO, Optional, Union, get_args

from pythonwrench.cast import as_builtin
from pythonwrench.functools import function_alias
from pythonwrench.serialization._core import (
    OnError,
    OnExists,
    _dump_base,
    _dumps_base,
    _load_base,
    _loads_base,
    _save_base,
)

__all__ = [
    "dump_pickle",
    "dumps_pickle",
    "load_pickle",
    "loads_pickle",
    "read_pickle",
    "save_pickle",
]

# -- Dump / Save / Serialize content to PICKLE --


def dump_pickle(
    data: Any,
    target: Union[str, Path, os.PathLike, BinaryIO, None] = None,
    /,
    *,
    on_exists: Optional[OnExists] = None,
    overwrite: Optional[bool] = None,
    make_parents: bool = True,
    to_builtins: bool = False,
    **pkl_dumps_kwds,
) -> bytes:
    r"""Dump content to PICKLE format into bytes and/or file.

    Args:
        data: Data to dump to PICKLE.
        target: Optional filepath to save dumped data. Not used if None. defaults to None.
        on_exists: Define how target file should be treated if already exists. defaults to "overwrite".
        overwrite: (DEPRECATED: use on_exists instead) If True, overwrite target filepath. defaults to None.
        make_parents: Build intermediate directories to filepath. defaults to True.
        to_builtins: If True, converts data to builtin equivalent before saving. defaults to False.
        \*\*pkl_dumps_kwds: Other args passed to `pickle.dumps`.

    Returns:
        Dumped content as bytes.
    """
    return _dump_base(
        _serialize_pickle,
        "binary",
        data,
        target,
        on_exists=on_exists,
        overwrite=overwrite,
        make_parents=make_parents,
        to_builtins=to_builtins,
        **pkl_dumps_kwds,
    )


def dumps_pickle(
    data: Any,
    /,
    *,
    to_builtins: bool = False,
    **pkl_dumps_kwds,
) -> bytes:
    r"""Dump content to PICKLE format into bytes.

    Args:
        data: Data to dump to PICKLE.
        to_builtins: If True, converts data to builtin equivalent before saving. defaults to False.
        \*\*pkl_dumps_kwds: Other args passed to `pickle.dumps`.

    Returns:
        Dumped content as bytes.
    """
    return _dumps_base(
        _serialize_pickle,
        "binary",
        data,
        to_builtins=to_builtins,
        **pkl_dumps_kwds,
    )


def save_pickle(
    data: Any,
    target: Union[str, Path, PathLike, BinaryIO],
    /,
    *,
    on_exists: Optional[OnExists] = None,
    overwrite: Optional[bool] = None,
    make_parents: bool = True,
    to_builtins: bool = False,
    **pkl_dumps_kwds,
) -> None:
    r"""Dump content to PICKLE format into file.

    Args:
        data: Data to dump to PICKLE.
        target: Filepath to save dumped data.
        on_exists: Define how target file should be treated if already exists. defaults to "overwrite".
        overwrite: (DEPRECATED: use on_exists instead) If True, overwrite target filepath. defaults to None.
        make_parents: Build intermediate directories to filepath. defaults to True.
        to_builtins: If True, converts data to builtin equivalent before saving. defaults to False.
        \*\*pkl_dumps_kwds: Other args passed to `pickle.dumps`.
    """
    return _save_base(
        _serialize_pickle,
        "binary",
        data,
        target,
        on_exists=on_exists,
        overwrite=overwrite,
        make_parents=make_parents,
        to_builtins=to_builtins,
        **pkl_dumps_kwds,
    )


# -- Load / Read / Parse PICKLE content --


def load_pickle(
    source: Union[str, Path, BinaryIO],
    /,
    *,
    on_error: OnError = "raise",
    default: Any = None,
    **pkl_loads_kwds,
) -> Any:
    r"""Load content from PICKLE file.

    Args:
        file: Filepath file path.
        on_error: Defines how error should be handled.
            If "raise", raise the exception if file is not found or content is malformed JSON format.
            If "return_default", return the value provided by default argument.
        default: Value to return when on_error="return_default".
        \*\*pkl_loads_kwds: Other args passed to `pickle.loads`.
    """
    return _load_base(
        _parse_pickle,
        "binary",
        source,
        on_error=on_error,
        default=default,
        **pkl_loads_kwds,
    )


def loads_pickle(
    source: bytes,
    /,
    *,
    on_error: OnError = "raise",
    default: Any = None,
    **pkl_loads_kwds,
) -> Any:
    r"""Load content from raw bytes.

    Args:
        source: Encoded elements bytes.
        on_error: Defines how error should be handled.
            If "raise", raise the exception if file is not found or content is malformed JSON format.
            If "return_default", return the value provided by default argument.
        default: Value to return when on_error="return_default".
        \*\*pkl_loads_kwds: Other args passed to `pickle.loads`.
    """
    return _loads_base(
        _parse_pickle,
        "binary",
        source,
        on_error=on_error,
        default=default,
        **pkl_loads_kwds,
    )


@function_alias(load_pickle)
def read_pickle(*args, **kwargs): ...


def _serialize_pickle(
    data: Any,
    buffer: BinaryIO,
    /,
    *,
    to_builtins: bool = False,
    **pkl_dump_kwds,
) -> None:
    if to_builtins:
        data = as_builtin(data)
    pickle.dump(data, buffer, **pkl_dump_kwds)


def _parse_pickle(
    buffer: BinaryIO,
    /,
    *,
    on_error: OnError = "raise",
    default: Any = None,
    **pkl_loads_kwds,
) -> Any:
    try:
        return pickle.load(buffer, **pkl_loads_kwds)
    except (UnpicklingError, EOFError):
        if on_error == "raise":
            raise
        elif on_error in ("return_default", "default"):
            return default
        else:
            msg = f"Invalid argument {on_error=}. (expected one of {get_args(OnError)})"
            raise ValueError(msg)
