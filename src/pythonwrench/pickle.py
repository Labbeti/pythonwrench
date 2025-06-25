#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pickle
from io import BufferedReader, BufferedWriter
from pathlib import Path
from typing import Any, Union

from pythonwrench.cast import as_builtin
from pythonwrench.io import _setup_output_fpath


def dump_pickle(
    data: Any,
    fpath: Union[str, Path, os.PathLike, None, BufferedWriter],
    *,
    overwrite: bool = True,
    make_parents: bool = True,
    to_builtins: bool = False,
    **pkl_dumps_kwds,
) -> bytes:
    """Dump data to pickle format."""
    if isinstance(fpath, (str, Path, os.PathLike)):
        fpath = _setup_output_fpath(fpath, overwrite, make_parents)
        with fpath.open("wb") as file:
            return dump_pickle(
                data,
                file,
                overwrite=overwrite,
                make_parents=make_parents,
                to_builtins=to_builtins,
                **pkl_dumps_kwds,
            )

    if to_builtins:
        data = as_builtin(data)
    content = pickle.dumps(data)

    if isinstance(fpath, BufferedWriter):
        fpath.write(content)

    return content


def load_pickle(fpath: Union[str, Path, BufferedReader], **pkl_loads_kwds) -> Any:
    """Load and parse pickle file."""
    if isinstance(fpath, (str, Path, os.PathLike)):
        fpath = Path(fpath)
        with fpath.open("rb") as file:
            return load_pickle(file, **pkl_loads_kwds)

    content = fpath.read()
    return _parse_pickle(content, **pkl_loads_kwds)


def _parse_pickle(content: bytes, **pkl_loads_kwds) -> Any:
    return pickle.loads(content, **pkl_loads_kwds)
