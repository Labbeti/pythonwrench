#!/usr/bin/env python

import os
from io import BytesIO, IOBase, TextIOBase, TextIOWrapper
from pathlib import Path
from typing import (
    Any,
    Generic,
    Literal,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    Union,
    overload,
)

from pythonwrench.warnings import warn_once

OnError = Literal["raise", "return_default"]
OnExists = Literal["overwrite", "skip", "raise"]

T_IOType = TypeVar("T_IOType", TextIOBase, BytesIO)
T_ContentType = TypeVar("T_ContentType", str, bytes, contravariant=True)


class SupportsWrite(Protocol[T_ContentType]):
    def write(self, s: T_ContentType, /) -> object: ...


class _BufferDuplicate(IOBase, Generic[T_IOType, T_ContentType]):
    # TODO: use this class for serialization functions to store into file+buffer
    @overload
    def __init__(
        self: "_BufferDuplicate[TextIOBase, str]",
        *buffers: TextIOBase,
    ) -> None: ...

    @overload
    def __init__(
        self: "_BufferDuplicate[BytesIO, bytes]",
        *buffers: BytesIO,
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


@overload
def _setup_output_fpath(
    fpath: Union[str, Path, os.PathLike],
    *,
    on_exists: OnExists = "overwrite",
    overwrite: Optional[bool] = None,
    make_parents: bool = True,
    absolute: bool = True,
) -> Path:
    """Perform the setup output fpath operation."""


@overload
def _setup_output_fpath(
    fpath: TextIOWrapper,
    *,
    on_exists: OnExists = "overwrite",
    overwrite: Optional[bool] = None,
    make_parents: bool = True,
    absolute: bool = True,
) -> TextIOWrapper:
    """Perform the setup output fpath operation."""


@overload
def _setup_output_fpath(
    fpath: None,
    *,
    on_exists: OnExists = "overwrite",
    overwrite: Optional[bool] = None,
    make_parents: bool = True,
    absolute: bool = True,
) -> None:
    """Perform the setup output fpath operation."""


def _setup_output_fpath(
    fpath: Union[str, Path, os.PathLike, TextIOWrapper, None],
    *,
    on_exists: OnExists = "overwrite",
    overwrite: Optional[bool] = None,
    make_parents: bool = True,
    absolute: bool = True,
) -> Union[Path, None, TextIOWrapper]:
    """Resolve path, expand path and create intermediate parents."""
    if not isinstance(fpath, (str, Path, os.PathLike)):
        return fpath

    on_exists, overwrite = _resolve_on_exists(on_exists, overwrite)

    fpath = Path(fpath)
    if absolute:
        fpath = fpath.resolve().expanduser()

    if make_parents and not fpath.exists():
        fpath.parent.mkdir(parents=True, exist_ok=True)
    elif on_exists == "raise" and fpath.exists():
        msg = f"Target CSV file already exists: {fpath}. (with {on_exists=})"
        raise FileExistsError(msg)

    return fpath


def _resolve_on_exists(
    on_exists: Optional[OnExists],
    overwrite: Optional[bool],
) -> Tuple[OnExists, Optional[bool]]:
    if isinstance(overwrite, bool):
        warn_once(f"Depreacted arg {overwrite=}. Use 'on_exists' instead.")
        on_exists = "overwrite" if overwrite else "skip"
        overwrite = None
    elif on_exists is None:
        on_exists = "overwrite"
    return on_exists, overwrite
