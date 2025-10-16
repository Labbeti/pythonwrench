#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from io import StringIO, TextIOBase
from os import PathLike
from pathlib import Path
from typing import Any, Optional, Union

from pythonwrench._core import _setup_output_fpath
from pythonwrench.cast import as_builtin
from pythonwrench.functools import function_alias

# -- Dump / Save / Serialize content to JSON --


def dump_json(
    data: Any,
    file: Union[str, Path, None, TextIOBase] = None,
    /,
    *,
    overwrite: bool = True,
    make_parents: bool = True,
    to_builtins: bool = False,
    # JSON dump kwargs
    indent: Optional[int] = 4,
    ensure_ascii: bool = False,
    **json_dumps_kwds,
) -> str:
    r"""Dump content to JSON format into a string and/or file.

    Args:
        data: Data to dump to JSON.
        file: Optional filepath to save dumped data. Not used if None. defaults to None.
        overwrite: If True, overwrite target filepath. defaults to True.
        make_parents: Build intermediate directories to filepath. defaults to True.
        to_builtins: If True, converts data to builtin equivalent before saving. defaults to False.
        indent: JSON indentation size in spaces. defaults to 4.
        ensure_ascii: Ensure only ASCII characters. defaults to False.
        \*\*json_dump_kwds: Other args passed to `json.dumps`.

    Returns:
        Dumped content as string.
    """
    content = dumps_json(
        data,
        to_builtins=to_builtins,
        indent=indent,
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


def dumps_json(
    data: Any,
    /,
    *,
    to_builtins: bool = False,
    # JSON dump kwargs
    indent: Optional[int] = 4,
    ensure_ascii: bool = False,
    **json_dumps_kwds,
) -> str:
    with StringIO() as buffer:
        _serialize_json(
            data,
            buffer,
            to_builtins=to_builtins,
            indent=indent,
            ensure_ascii=ensure_ascii,
            **json_dumps_kwds,
        )
        content = buffer.getvalue()
    return content


def save_json(
    data: Any,
    file: Union[str, Path, PathLike, TextIOBase],
    /,
    *,
    overwrite: bool = True,
    make_parents: bool = True,
    to_builtins: bool = False,
    # JSON dump kwargs
    indent: Optional[int] = 4,
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

    _serialize_json(
        data,
        file,
        to_builtins=to_builtins,
        indent=indent,
        ensure_ascii=ensure_ascii,
        **json_dumps_kwds,
    )

    if close:
        file.close()


def _serialize_json(
    data: Any,
    buffer: TextIOBase,
    /,
    *,
    to_builtins: bool = False,
    **json_dumps_kwds,
) -> None:
    if to_builtins:
        data = as_builtin(data)
    return json.dump(data, buffer, **json_dumps_kwds)


# -- Load / Read / Parse JSON content --


def load_json(
    file: Union[str, Path, PathLike, TextIOBase],
    /,
    **json_loads_kwds,
) -> Any:
    if isinstance(file, (str, Path, PathLike)):
        file = open(file, "r")
        close = True
    else:
        close = False

    data = _parse_json(file, **json_loads_kwds)
    if close:
        file.close()
    return data


def loads_json(content: str, /, **json_loads_kwds) -> Any:
    with StringIO(content) as buffer:
        return _parse_json(buffer, **json_loads_kwds)


@function_alias(load_json)
def read_json(*args, **kwargs): ...


def _parse_json(buffer: TextIOBase, **json_loads_kwds) -> Any:
    return json.load(buffer, **json_loads_kwds)
