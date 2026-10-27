#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from io import BytesIO, TextIOBase, TextIOWrapper
from pathlib import Path
from typing import (
    Any,
    Generic,
    Literal,
    Tuple,
    TypeVar,
    Union,
    overload,
)

OnError = Literal["raise", "return_default"]
OnExist = Literal["overwrite", "skip", "raise"]

T_IOType = TypeVar("T_IOType", TextIOBase, BytesIO)
T_ContentType = TypeVar("T_ContentType", str, bytes)


class _BufferDuplicate(Generic[T_IOType, T_ContentType]):
    @overload
    def __init__(
        self: "_BufferDuplicate[TextIOBase, str]", *buffers: TextIOBase
    ) -> None: ...

    @overload
    def __init__(
        self: "_BufferDuplicate[BytesIO, bytes]", *buffers: BytesIO
    ) -> None: ...

    def __init__(self, *buffers: Any) -> None:
        super().__init__()
        self._buffers: Tuple[T_IOType, ...] = buffers

    def write(self, /, x: T_ContentType) -> int:
        total = 0
        for buffer in self._buffers:
            n = buffer.write(x)  # type: ignore
            total += n
        return total


file = open("dhqzudh")
buffer = _BufferDuplicate(file)
buffer.write


@overload
def _setup_output_fpath(
    fpath: Union[str, Path, os.PathLike],
    *,
    overwrite: bool = True,
    make_parents: bool = True,
    absolute: bool = True,
) -> Path:
    """Perform the setup output fpath operation."""
    ...


@overload
def _setup_output_fpath(
    fpath: TextIOWrapper,
    *,
    overwrite: bool = True,
    make_parents: bool = True,
    absolute: bool = True,
) -> TextIOWrapper:
    """Perform the setup output fpath operation."""
    ...


@overload
def _setup_output_fpath(
    fpath: None,
    *,
    overwrite: bool = True,
    make_parents: bool = True,
    absolute: bool = True,
) -> None:
    """Perform the setup output fpath operation."""
    ...


def _setup_output_fpath(
    fpath: Union[str, Path, os.PathLike, TextIOWrapper, None],
    *,
    overwrite: bool = True,
    make_parents: bool = True,
    absolute: bool = True,
) -> Union[Path, None, TextIOWrapper]:
    """Resolve path, expand path and create intermediate parents."""
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
