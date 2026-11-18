#!/usr/bin/env python

import json
import os
from io import TextIOBase
from json import JSONDecodeError
from os import PathLike
from pathlib import Path
from typing import Any, Optional, Union, get_args

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
    "dump_json",
    "dumps_json",
    "load_json",
    "loads_json",
    "read_json",
    "save_json",
]

# -- Dump / Save / Serialize content to JSON --


def dump_json(
    data: Any,
    target: Union[str, Path, None, TextIOBase] = None,
    /,
    *,
    on_exists: Optional[OnExists] = None,
    overwrite: Optional[bool] = None,
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
        target: Optional filepath to save dumped data. Not used if None. defaults to None.
        on_exists: Define how target file should be treated if already exists. defaults to "overwrite".
        overwrite: (DEPRECATED: use on_exists instead) If True, overwrite target filepath. defaults to None.
        make_parents: Build intermediate directories to filepath. defaults to True.
        to_builtins: If True, converts data to builtin equivalent before saving. defaults to False.
        indent: JSON indentation size in spaces. defaults to 4.
        ensure_ascii: Ensure only ASCII characters. defaults to False.
        \*\*json_dump_kwds: Other args passed to `json.dumps`.

    Returns:
        Dumped content as string.
    """
    return _dump_base(
        _serialize_json,
        "text",
        data,
        target,
        on_exists=on_exists,
        overwrite=overwrite,
        make_parents=make_parents,
        to_builtins=to_builtins,
        indent=indent,
        ensure_ascii=ensure_ascii,
        **json_dumps_kwds,
    )


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
    r"""Dump content to JSON format into a string and/or file.

    Args:
        data: Data to dump to JSON.
        to_builtins: If True, converts data to builtin equivalent before saving. defaults to False.
        indent: JSON indentation size in spaces. defaults to 4.
        ensure_ascii: Ensure only ASCII characters. defaults to False.
        \*\*json_dump_kwds: Other args passed to `json.dump`.

    Returns:
        Dumped content as string.
    """
    return _dumps_base(
        _serialize_json,
        "text",
        data,
        to_builtins=to_builtins,
        indent=indent,
        ensure_ascii=ensure_ascii,
        **json_dumps_kwds,
    )


def save_json(
    data: Any,
    target: Union[str, Path, PathLike, TextIOBase],
    /,
    *,
    on_exists: Optional[OnExists] = None,
    overwrite: Optional[bool] = None,
    make_parents: bool = True,
    to_builtins: bool = False,
    # JSON dump kwargs
    indent: Optional[int] = 4,
    ensure_ascii: bool = False,
    **json_dumps_kwds,
) -> None:
    r"""Save data to JSON file.

    Args:
        data: Data to dump to JSON.
        target: Target file.
        on_exists: Define how target file should be treated if already exists. defaults to "overwrite".
        overwrite: (DEPRECATED: use on_exists instead) If True, overwrite target filepath. defaults to None.
        make_parents: Build intermediate directories to filepath. defaults to True.
        to_builtins: If True, converts data to builtin equivalent before saving. defaults to False.
        indent: JSON indentation size in spaces. defaults to 4.
        ensure_ascii: Ensure only ASCII characters. defaults to False.
        \*\*json_dump_kwds: Other args passed to `json.dump`.
    """
    return _save_base(
        _serialize_json,
        "text",
        data,
        target,
        on_exists=on_exists,
        overwrite=overwrite,
        make_parents=make_parents,
        to_builtins=to_builtins,
        indent=indent,
        ensure_ascii=ensure_ascii,
        **json_dumps_kwds,
    )


# -- Load / Read / Parse JSON content --


def load_json(
    target: Union[str, Path, os.PathLike, TextIOBase],
    /,
    *,
    on_error: OnError = "raise",
    default: Any = None,
    **json_loads_kwds,
) -> Any:
    r"""Load JSON file.

    Args:
        target: Target filepath or buffer to read.
        on_error: Defines how error should be handled.
            If "raise", raise the exception if file is not found or content is malformed JSON format.
            If "return_default", return the value provided by default argument.
        default: Value to return when on_error="return_default".
        \*\*json_loads_kwds: Other args passed to `json.load`.
    """
    return _load_base(
        _parse_json,
        "text",
        target,
        on_error=on_error,
        default=default,
        **json_loads_kwds,
    )


def loads_json(
    content: str,
    /,
    *,
    on_error: OnError = "raise",
    default: Any = None,
    **json_loads_kwds,
) -> Any:
    r"""Load JSON from string.

    Args:
        content: Source content.
        on_error: Defines how error should be handled.
            If "raise", raise the exception if file is not found or content is malformed JSON format.
            If "return_default", return the value provided by default argument.
        default: Value to return when on_error="return_default".
        \*\*json_loads_kwds: Other args passed to `json.load`.
    """
    return _loads_base(
        _parse_json,
        "text",
        content,
        on_error=on_error,
        default=default,
        **json_loads_kwds,
    )


@function_alias(load_json)
def read_json(*args, **kwargs): ...


def _serialize_json(
    data: Any,
    buffer: TextIOBase,
    /,
    *,
    to_builtins: bool = False,
    **json_dumps_kwds,
) -> None:
    """Perform the serialize json operation."""
    if to_builtins:
        data = as_builtin(data)
    return json.dump(data, buffer, **json_dumps_kwds)


def _parse_json(
    buffer: TextIOBase,
    *,
    on_error: OnError,
    default: Any = None,
    **json_loads_kwds,
) -> Any:
    """Parse json."""
    try:
        return json.load(buffer, **json_loads_kwds)
    except JSONDecodeError:
        if on_error == "raise":
            raise
        elif on_error in ("return_default", "default"):
            return default
        else:
            msg = f"Invalid argument {on_error=}. (expected one of {get_args(OnError)})"
            raise ValueError(msg)
