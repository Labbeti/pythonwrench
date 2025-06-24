#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from pathlib import Path
from typing import Any, Optional, Union

from pythonwrench.io import _setup_path


def dump_json(
    data: Any,
    fpath: Union[str, Path, None] = None,
    *,
    overwrite: bool = True,
    make_parents: bool = True,
    # JSON dump kwargs
    indent: Optional[int] = 4,
    ensure_ascii: bool = False,
    **json_dump_kwds,
) -> str:
    """Dump content to JSON format into a string and/or file.

    Args:
        data: Data to dump to JSON.
        fpath: Optional filepath to save dumped data. Not used if None. defaults to None.
        overwrite: If True, overwrite target filepath. defaults to True.
        make_parents: Build intermediate directories to filepath. defaults to True.
        indent: JSON indentation size in spaces. defaults to 4.
        ensure_ascii: Ensure only ASCII characters. defaults to False.
        **json_dump_kwds: Other `json.dump` args.

    Returns:
        Dumped content as string.
    """
    fpath = _setup_path(fpath, overwrite, make_parents)
    content = json.dumps(
        data,
        indent=indent,
        ensure_ascii=ensure_ascii,
        **json_dump_kwds,
    )
    if fpath is not None:
        fpath.write_text(content)
    return content


def load_json(fpath: Union[str, Path], **json_load_kwds) -> Any:
    fpath = Path(fpath)
    content = fpath.read_text()
    return _parse_json(content)


def _parse_json(content: str, **json_load_kwds) -> Any:
    return json.loads(content, **json_load_kwds)
