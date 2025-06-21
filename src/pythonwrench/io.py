#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from pathlib import Path
from typing import Optional, TypeVar, Union

T = TypeVar("T", covariant=True)


def _setup_path(
    fpath: Union[str, Path, os.PathLike, None],
    overwrite: bool,
    make_parents: bool,
    absolute: bool = True,
) -> Optional[Path]:
    """Resolve & expand path and create intermediate parents."""
    if not isinstance(fpath, (str, Path, os.PathLike)):
        return fpath

    fpath = Path(fpath)
    if absolute:
        fpath = fpath.resolve().expanduser()

    if not overwrite and fpath.exists():
        msg = f"File {fpath} already exists."
        raise FileExistsError(msg)
    elif make_parents:
        fpath.parent.mkdir(parents=True, exist_ok=True)

    return fpath
