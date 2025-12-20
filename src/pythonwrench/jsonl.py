#!/usr/bin/env python
# -*- coding: utf-8 -*-

from io import StringIO, TextIOBase
from os import PathLike
from pathlib import Path
from typing import Union

from pythonwrench._core import _setup_output_fpath
from pythonwrench.cast import as_builtin
from pythonwrench.functools import function_alias
from pythonwrench.json import (
    _serialize_json,
    dumps_json,
    load_json,
    loads_json,
)
from pythonwrench.semver import Version
from pythonwrench.warnings import warn_once

__all__ = [
    "dump_jsonl",
    "dumps_jsonl",
    "save_jsonl",
    "load_jsonl",
    "loads_jsonl",
    "read_jsonl",
]

# -- Dump / Save / Serialize content to JSONL --


def dump_jsonl(
    data: list,
    file: Union[str, Path, None, TextIOBase] = None,
    /,
    *,
    overwrite: bool = True,
    make_parents: bool = True,
    to_builtins: bool = False,
    # JSON dump kwargs
    ensure_ascii: bool = False,
    **json_dumps_kwds,
) -> str:
    r"""Dump content to JSONL format into a string and/or file.

    Args:
        data: Data to dump to JSONL.
        file: Optional filepath to save dumped data. Not used if None. defaults to None.
        overwrite: If True, overwrite target filepath. defaults to True.
        make_parents: Build intermediate directories to filepath. defaults to True.
        to_builtins: If True, converts data to builtin equivalent before saving. defaults to False.
        ensure_ascii: Ensure only ASCII characters. defaults to False.
        \*\*json_dump_kwds: Other args passed to `json.dumps`.

    Returns:
        Dumped content as string.
    """
    content = dumps_json(
        data,
        to_builtins=to_builtins,
        ensure_ascii=ensure_ascii,
        **json_dumps_kwds,
    )

    if isinstance(file, (str, Path, PathLike)):
        file = _setup_output_fpath(file, overwrite, make_parents)
        with open(file, "w") as opened_file:
            opened_file.write(content)
    elif isinstance(file, TextIOBase):
        file.write(content)
    elif file is None:
        pass
    else:
        msg = f"Invalid argument type {type(file)}. (expected one of str, Path, TextIOBase, None)"
        raise TypeError(msg)

    return content


def dumps_jsonl(
    data: list,
    /,
    *,
    to_builtins: bool = False,
    # JSON dump kwargs
    ensure_ascii: bool = False,
    **json_dumps_kwds,
) -> str:
    with StringIO() as buffer:
        _serialize_jsonl(
            data,
            buffer,
            to_builtins=to_builtins,
            ensure_ascii=ensure_ascii,
            **json_dumps_kwds,
        )
        content = buffer.getvalue()
    return content


def save_jsonl(
    data: list,
    file: Union[str, Path, PathLike, TextIOBase],
    /,
    *,
    overwrite: bool = True,
    make_parents: bool = True,
    to_builtins: bool = False,
    # JSON dump kwargs
    ensure_ascii: bool = False,
    **json_dumps_kwds,
) -> None:
    if isinstance(file, (str, Path, PathLike)):
        file = _setup_output_fpath(file, overwrite=overwrite, make_parents=make_parents)
        file = open(file, "w")
        close = True
    elif isinstance(file, TextIOBase):
        close = False
    else:
        msg = f"Invalid argument type {type(file)}. (expected one of str, Path, PathLike, TextIOBase)"
        raise TypeError(msg)

    _serialize_jsonl(
        data,
        file,
        to_builtins=to_builtins,
        ensure_ascii=ensure_ascii,
        **json_dumps_kwds,
    )

    if close:
        file.close()


def _serialize_jsonl(
    data: list,
    buffer: TextIOBase,
    /,
    *,
    to_builtins: bool = False,
    **json_dumps_kwds,
) -> None:
    if to_builtins:
        data = as_builtin(data)

    indent = json_dumps_kwds.get("indent", None)
    if indent is not None:
        warn_once(f"Invalid argument {indent=}. It will be replaced by indent=None")
        json_dumps_kwds["indent"] = None

    for data_i in data:
        _serialize_json(data_i, buffer, to_builtins=False, **json_dumps_kwds)
        buffer.write("\n")


# -- Load / Read / Parse JSONL content --


def load_jsonl(
    file: Union[str, Path, PathLike, TextIOBase],
    /,
    **json_loads_kwds,
) -> list:
    if isinstance(file, (str, Path, PathLike)):
        file = open(file, "r")
        close = True
    else:
        close = False

    data = _parse_jsonl(file, **json_loads_kwds)
    if close:
        file.close()
    return data


def loads_jsonl(content: str, /, **json_loads_kwds) -> list:
    with StringIO(content) as buffer:
        return _parse_jsonl(buffer, **json_loads_kwds)


@function_alias(load_json)
def read_jsonl(*args, **kwargs): ...


def _parse_jsonl(buffer: TextIOBase, **json_loads_kwds) -> list:
    data_lst = []
    while True:
        content = buffer.readline()
        if content == "":
            break
        content = _removesuffix(content, "\n")
        data = loads_json(content, **json_loads_kwds)
        data_lst.append(data)
    return data_lst


def _removesuffix(x: str, suffix: str) -> str:
    """Equivalent to str.removesuffix for python < 3.9.0."""
    if Version.python() >= Version("3.9.0"):
        return x.removesuffix(suffix)

    size = len(suffix)
    if x[size:] != suffix:
        return x
    else:
        return x[:size]
