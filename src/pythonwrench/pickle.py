#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pickle
from pathlib import Path
from typing import Any, Union

from pythonwrench.io import _setup_path


def dump_pickle(
    obj: Any,
    fpath: Union[str, Path, os.PathLike, None],
    *,
    overwrite: bool = True,
    make_parents: bool = True,
) -> bytes:
    fpath = _setup_path(fpath, overwrite, make_parents)
    content = pickle.dumps(obj)
    if isinstance(fpath, Path):
        fpath.write_bytes(content)
    return content


def load_pickle(fpath: Union[str, Path], **pkl_loads_kwds) -> Any:
    fpath = Path(fpath)
    content = fpath.read_bytes()
    return _parse_pickle(content, **pkl_loads_kwds)


def _parse_pickle(content: bytes, **pkl_loads_kwds) -> Any:
    return pickle.loads(content, **pkl_loads_kwds)
