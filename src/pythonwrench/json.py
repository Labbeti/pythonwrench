#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from io import TextIOWrapper
from pathlib import Path
from typing import Any, Optional, Union

from pythonwrench.cast import as_builtin
from pythonwrench.io import _setup_output_fpath


def dump_json(
    data: Any,
    fpath: Union[str, Path, None, TextIOWrapper] = None,
    *,
    overwrite: bool = True,
    make_parents: bool = True,
    to_builtins: bool = False,
    # JSON dump kwargs
    indent: Optional[int] = 4,
    ensure_ascii: bool = False,
    **json_dumps_kwds,
) -> str:
    """Dump content to JSON format into a string and/or file.

    Args:
        data: Data to dump to JSON.
        fpath: Optional filepath to save dumped data. Not used if None. defaults to None.
        overwrite: If True, overwrite target filepath. defaults to True.
        make_parents: Build intermediate directories to filepath. defaults to True.
        to_builtins: If True, converts data to builtin equivalent before saving. defaults to False.
        indent: JSON indentation size in spaces. defaults to 4.
        ensure_ascii: Ensure only ASCII characters. defaults to False.
        **json_dump_kwds: Other args passed to `json.dumps`.

    Returns:
        Dumped content as string.
    """
    if isinstance(fpath, (str, Path)):
        fpath = _setup_output_fpath(fpath, overwrite, make_parents)

        with fpath.open("w") as file:
            return dump_json(
                data,
                file,
                overwrite=overwrite,
                make_parents=make_parents,
                to_builtins=to_builtins,
                indent=indent,
                ensure_ascii=ensure_ascii,
                **json_dumps_kwds,
            )

    if to_builtins:
        data = as_builtin(data)

    content = json.dumps(
        data,
        indent=indent,
        ensure_ascii=ensure_ascii,
        **json_dumps_kwds,
    )
    if isinstance(fpath, TextIOWrapper):
        fpath.write(content)

    return content


def load_json(fpath: Union[str, Path, TextIOWrapper], **json_loads_kwds) -> Any:
    if isinstance(fpath, (str, Path)):
        fpath = Path(fpath)
        with fpath.open("r") as file:
            return load_json(file, **json_loads_kwds)

    elif isinstance(fpath, TextIOWrapper):
        content = fpath.read()
        return _parse_json(content, **json_loads_kwds)

    else:
        msg = f"Invalid argument type {type(fpath)}."
        raise TypeError(msg)


def _parse_json(content: str, **json_loads_kwds) -> Any:
    return json.loads(content, **json_loads_kwds)
