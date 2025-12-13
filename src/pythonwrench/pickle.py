#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pickle
from io import BytesIO
from os import PathLike
from pathlib import Path
from typing import Any, BinaryIO, Union

from pythonwrench._core import _setup_output_fpath
from pythonwrench.cast import as_builtin
from pythonwrench.functools import function_alias

# -- Dump / Save / Serialize content to PICKLE --


def dump_pickle(
    data: Any,
    file: Union[str, Path, os.PathLike, BinaryIO, None] = None,
    /,
    *,
    overwrite: bool = True,
    make_parents: bool = True,
    to_builtins: bool = False,
    **pkl_dumps_kwds,
) -> bytes:
    r"""Dump content to PICKLE format into bytes and/or file.

    Args:
        data: Data to dump to PICKLE.
        file: Optional filepath to save dumped data. Not used if None. defaults to None.
        overwrite: If True, overwrite target filepath. defaults to True.
        make_parents: Build intermediate directories to filepath. defaults to True.
        to_builtins: If True, converts data to builtin equivalent before saving. defaults to False.
        \*\*pkl_dumps_kwds: Other args passed to `pickle.dumps`.

    Returns:
        Dumped content as bytes.
    """
    content = dumps_pickle(
        data,
        to_builtins=to_builtins,
        **pkl_dumps_kwds,
    )

    if isinstance(file, (str, Path, PathLike)):
        file = _setup_output_fpath(file, overwrite, make_parents)
        with open(file, "wb") as opened_file:
            opened_file.write(content)
    elif isinstance(file, BinaryIO):
        file.write(content)
    elif file is None:
        pass
    else:
        msg = f"Invalid argument type {type(file)}. (expected one of str, Path, TextIOBase, None)"
        raise TypeError(msg)

    return content


def dumps_pickle(
    data: Any,
    /,
    *,
    to_builtins: bool = False,
    **pkl_dumps_kwds,
) -> bytes:
    with BytesIO() as buffer:
        _serialize_pickle(
            data,
            buffer,
            to_builtins=to_builtins,
            **pkl_dumps_kwds,
        )
        content = buffer.getvalue()
    return content


def save_pickle(
    data: Any,
    file: Union[str, Path, PathLike, BinaryIO],
    /,
    *,
    overwrite: bool = True,
    make_parents: bool = True,
    to_builtins: bool = False,
    **pkl_dumps_kwds,
) -> None:
    if isinstance(file, (str, Path, PathLike)):
        file = _setup_output_fpath(file, overwrite=overwrite, make_parents=make_parents)
        file = open(file, "wb")
        close = True
    elif isinstance(file, BinaryIO):
        close = False
    else:
        msg = f"Invalid argument type {type(file)}. (expected one of str, Path, PathLike, TextIOBase)"
        raise TypeError(msg)

    _serialize_pickle(
        data,
        file,
        to_builtins=to_builtins,
        **pkl_dumps_kwds,
    )

    if close:
        file.close()


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
    return pickle.dump(data, buffer, **pkl_dump_kwds)


# -- Load / Read / Parse PICKLE content --


def load_pickle(file: Union[str, Path, BinaryIO], /, **pkl_loads_kwds) -> Any:
    if isinstance(file, (str, Path, PathLike)):
        file = open(file, "rb")
        close = True
    else:
        close = False

    data = _parse_pickle(file, **pkl_loads_kwds)
    if close:
        file.close()
    return data


def loads_pickle(content: bytes, /, **pkl_loads_kwds) -> Any:
    with BytesIO(content) as buffer:
        return _parse_pickle(buffer, **pkl_loads_kwds)


@function_alias(load_pickle)
def read_pickle(*args, **kwargs): ...


def _parse_pickle(buffer: BinaryIO, **pkl_loads_kwds) -> Any:
    return pickle.load(buffer, **pkl_loads_kwds)
