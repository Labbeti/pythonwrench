#!/usr/bin/env python

from io import TextIOBase
from os import PathLike
from pathlib import Path
from typing import Any, Optional, Union

from pythonwrench.cast import as_builtin
from pythonwrench.functools import function_alias
from pythonwrench.semver import Version
from pythonwrench.serialization._core import (
    OnError,
    OnExists,
    _dump_base,
    _dumps_base,
    _load_base,
    _loads_base,
    _save_base,
)
from pythonwrench.serialization.json import (
    _serialize_json,
    load_json,
    loads_json,
)
from pythonwrench.warnings import warn_once

__all__ = [
    "dump_jsonl",
    "dumps_jsonl",
    "load_jsonl",
    "loads_jsonl",
    "read_jsonl",
    "save_jsonl",
]

# -- Dump / Save / Serialize content to JSONL --


def dump_jsonl(
    data: list,
    target: Union[str, Path, None, TextIOBase] = None,
    /,
    *,
    on_exists: Optional[OnExists] = None,
    overwrite: Optional[bool] = None,
    make_parents: bool = True,
    to_builtins: bool = False,
    # JSON dump kwargs
    ensure_ascii: bool = False,
    **json_dumps_kwds,
) -> str:
    r"""Dump content to JSONL format into a string and/or file.

    Args:
        data: Data to dump to JSONL.
        target: Optional filepath to save dumped data. Not used if None. defaults to None.
        on_exists: Define how target file should be treated if already exists. defaults to "overwrite".
        overwrite: (DEPRECATED: use on_exists instead) If True, overwrite target filepath. defaults to None.
        make_parents: Build intermediate directories to filepath. defaults to True.
        to_builtins: If True, converts data to builtin equivalent before saving. defaults to False.
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
        ensure_ascii=ensure_ascii,
        **json_dumps_kwds,
    )


def dumps_jsonl(
    source: list,
    /,
    *,
    to_builtins: bool = False,
    # JSON dump kwargs
    ensure_ascii: bool = False,
    **json_dumps_kwds,
) -> str:
    r"""Dump content to JSONL format into a string and/or file.

    Args:
        data: Data to dump to JSON.
        to_builtins: If True, converts data to builtin equivalent before saving. defaults to False.
        \*\*json_dump_kwds: Other args passed to `json.dump`.

    Returns:
        Dumped content as string.
    """
    return _dumps_base(
        _serialize_jsonl,
        "text",
        source,
        to_builtins=to_builtins,
        ensure_ascii=ensure_ascii,
        **json_dumps_kwds,
    )


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
    """Save jsonl."""
    return _save_base(
        _serialize_jsonl,
        "text",
        data,
        file,
        overwrite=overwrite,
        make_parents=make_parents,
        to_builtins=to_builtins,
        ensure_ascii=ensure_ascii,
        **json_dumps_kwds,
    )


# -- Load / Read / Parse JSONL content --


def load_jsonl(
    source: Union[str, Path, PathLike, TextIOBase],
    /,
    *,
    on_error: OnError = "raise",
    default: Any = None,
    **json_loads_kwds,
) -> list:
    r"""Load JSONL file.

    Args:
        target: Target filepath or buffer to read.
        on_error: Defines how error should be handled.
            If "raise", raise the exception if file is not found or content is malformed JSON format.
            If "return_default", return the value provided by default argument.
        default: Value to return when on_error="return_default".
        \*\*json_loads_kwds: Other args passed to `json.load`.
    """
    return _load_base(
        _parse_jsonl,
        "text",
        source,
        on_error=on_error,
        default=default,
        **json_loads_kwds,
    )


def loads_jsonl(
    source: str,
    /,
    *,
    on_error: OnError = "raise",
    default: Any = None,
    **json_loads_kwds,
) -> list:
    r"""Load JSONL from string.

    Args:
        source: Source content.
        on_error: Defines how error should be handled.
            If "raise", raise the exception if file is not found or content is malformed JSON format.
            If "return_default", return the value provided by default argument.
        default: Value to return when on_error="return_default".
        \*\*json_loads_kwds: Other args passed to `json.load`.
    """
    return _loads_base(
        _parse_jsonl,
        "text",
        source,
        on_error=on_error,
        default=default,
        **json_loads_kwds,
    )


@function_alias(load_json)
def read_jsonl(*args, **kwargs): ...


def _serialize_jsonl(
    data: list,
    buffer: TextIOBase,
    /,
    *,
    to_builtins: bool = False,
    **json_dumps_kwds,
) -> None:
    """Perform the serialize jsonl operation."""
    if to_builtins:
        data = as_builtin(data)

    indent = json_dumps_kwds.get("indent", None)
    if indent is not None:
        warn_once(f"Invalid argument {indent=}. It will be replaced by indent=None")
        json_dumps_kwds["indent"] = None

    for data_i in data:
        _serialize_json(data_i, buffer, to_builtins=False, **json_dumps_kwds)
        buffer.write("\n")


def _parse_jsonl(
    buffer: TextIOBase,
    /,
    *,
    on_error: OnError = "raise",
    default: Any = None,
    **json_loads_kwds,
) -> list:
    """Parse jsonl."""
    data_lst = []
    while True:
        content = buffer.readline()
        if content == "":
            break
        content = _removesuffix(content, "\n")
        data = loads_json(
            content, on_error=on_error, default=default, **json_loads_kwds
        )
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
