#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from io import TextIOWrapper
from pathlib import Path
from typing import TypeVar, Union, overload

T = TypeVar("T", covariant=True)


@overload
def _setup_output_fpath(
    fpath: Union[str, Path, os.PathLike],
    overwrite: bool,
    make_parents: bool,
    absolute: bool = True,
) -> Path: ...


@overload
def _setup_output_fpath(
    fpath: TextIOWrapper,
    overwrite: bool,
    make_parents: bool,
    absolute: bool = True,
) -> TextIOWrapper: ...


@overload
def _setup_output_fpath(
    fpath: None,
    overwrite: bool,
    make_parents: bool,
    absolute: bool = True,
) -> None: ...


def _setup_output_fpath(
    fpath: Union[str, Path, os.PathLike, TextIOWrapper, None],
    overwrite: bool,
    make_parents: bool,
    absolute: bool = True,
) -> Union[Path, None, TextIOWrapper]:
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
