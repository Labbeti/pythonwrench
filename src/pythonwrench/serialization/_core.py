#!/usr/bin/env python

import io
import os
from io import BytesIO, IOBase, TextIOBase, TextIOWrapper
from pathlib import Path
from typing import (
    Any,
    BinaryIO,
    Callable,
    Generic,
    Literal,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
    overload,
)

from pythonwrench.warnings import warn_once

DataType = Literal["text", "binary"]
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
        # breakpoint()
        for buffer in self._buffers:
            # x = copy.deepcopy(x)
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
        warn_once(f"Deprecated arg {overwrite=}. Use 'on_exists' instead.")
        on_exists = "overwrite" if overwrite else "skip"
        overwrite = None
    elif on_exists is None:
        on_exists = "overwrite"
    return on_exists, overwrite


def _resolve_datatype(
    datatype: DataType,
) -> Tuple[str, str, Union[Type[io.BytesIO], Type[io.StringIO]]]:
    if datatype == "binary":
        input_mode = "rb"
        output_mode = "wb"
        buffer_type = io.BytesIO
    elif datatype == "text":
        input_mode = "r"
        output_mode = "w"
        buffer_type = io.StringIO
    else:
        msg = f"Invalid argument {datatype=}. (expected one of {get_args(DataType)})"
        raise ValueError(msg)

    return input_mode, output_mode, buffer_type


@overload
def _dump_base(
    serialize_data_fn: Callable[..., None],
    datatype: Literal["text"],
    data: Any,
    target: Union[str, Path, os.PathLike, TextIOBase, None],
    /,
    *,
    on_exists: Optional[OnExists],
    overwrite: Optional[bool],
    make_parents: bool,
    **kwargs,
) -> str: ...


@overload
def _dump_base(
    serialize_data_fn: Callable[..., None],
    datatype: Literal["binary"],
    data: Any,
    target: Union[str, Path, os.PathLike, BinaryIO, None],
    /,
    *,
    on_exists: Optional[OnExists],
    overwrite: Optional[bool],
    make_parents: bool,
    **kwargs,
) -> bytes: ...


def _dump_base(
    serialize_data_fn: Callable[..., None],
    datatype: DataType,
    data: Any,
    target: Union[str, Path, os.PathLike, TextIOBase, BinaryIO, None],
    /,
    *,
    on_exists: Optional[OnExists],
    overwrite: Optional[bool],
    make_parents: bool,
    **kwargs,
) -> Union[str, bytes]:
    _, output_mode, buffer_type = _resolve_datatype(datatype)
    on_exists, overwrite = _resolve_on_exists(on_exists, overwrite)

    if isinstance(target, (str, Path, os.PathLike)):
        target = _setup_output_fpath(
            target,
            overwrite=overwrite,
            on_exists=on_exists,
            make_parents=make_parents,
        )
        with open(target, output_mode) as file:
            dumped = _dump_base(
                serialize_data_fn,
                datatype,  # type: ignore
                data,
                file,  # type: ignore
                overwrite=overwrite,
                on_exists=on_exists,
                make_parents=make_parents,
                **kwargs,
            )
            return dumped

    targets = []
    if target is None:
        ...
    elif isinstance(target, (TextIOBase, io.BufferedWriter)):
        targets.append(target)  # type: ignore
    else:
        raise TypeError(f"Invalid argument type {type(target)=}.")

    with buffer_type() as buffer:
        targets.append(buffer)
        target_router = _BufferDuplicate(*targets)  # type: ignore
        serialize_data_fn(
            data,
            target_router,
            **kwargs,
        )
        dumped = buffer.getvalue()
        return dumped


@overload
def _dumps_base(
    serialize_data_fn: Callable[..., None],
    datatype: Literal["text"],
    data: Any,
    **kwargs,
) -> str: ...


@overload
def _dumps_base(
    serialize_data_fn: Callable[..., None],
    datatype: Literal["binary"],
    data: Any,
    **kwargs,
) -> bytes: ...


def _dumps_base(
    serialize_data_fn: Callable[..., None],
    datatype: DataType,
    data: Any,
    **kwargs,
) -> Union[str, bytes]:
    _, _, buffer_type = _resolve_datatype(datatype)

    with buffer_type() as buffer:
        serialize_data_fn(
            data,
            buffer,
            **kwargs,
        )
        return buffer.getvalue()


@overload
def _save_base(
    serialize_data_fn: Callable[..., None],
    datatype: Literal["text"],
    data: Any,
    target: Union[str, Path, os.PathLike, TextIOBase],
    /,
    *,
    on_exists: Optional[OnExists],
    overwrite: Optional[bool],
    make_parents: bool,
    **kwargs,
) -> None: ...


@overload
def _save_base(
    serialize_data_fn: Callable[..., None],
    datatype: Literal["binary"],
    data: Any,
    target: Union[str, Path, os.PathLike, BinaryIO],
    /,
    *,
    on_exists: Optional[OnExists],
    overwrite: Optional[bool],
    make_parents: bool,
    **kwargs,
) -> None: ...


def _save_base(
    serialize_data_fn: Callable[..., None],
    datatype: DataType,
    data: Any,
    target: Union[str, Path, os.PathLike, TextIOBase, BinaryIO],
    /,
    *,
    on_exists: Optional[OnExists],
    overwrite: Optional[bool],
    make_parents: bool,
    **kwargs,
) -> None:
    on_exists, overwrite = _resolve_on_exists(on_exists, overwrite)
    _, output_mode, _ = _resolve_datatype(datatype)

    if isinstance(target, (str, Path, os.PathLike)):
        target = _setup_output_fpath(
            target,
            overwrite=overwrite,
            on_exists=on_exists,
            make_parents=make_parents,
        )
        with open(target, output_mode) as file:
            return serialize_data_fn(
                data,
                file,
                **kwargs,
            )

    elif isinstance(target, (TextIOBase, io.BufferedWriter)):
        return serialize_data_fn(
            data,
            target,
            **kwargs,
        )

    else:
        msg = f"Invalid argument type {type(target)=}."
        raise TypeError(msg)


@overload
def _load_base(
    parse_data_fn: Callable,
    datatype: Literal["text"],
    source: Union[str, Path, os.PathLike, TextIOBase],
    **kwargs,
) -> Any: ...


@overload
def _load_base(
    parse_data_fn: Callable,
    datatype: Literal["binary"],
    source: Union[str, Path, os.PathLike, BinaryIO],
    **kwargs,
) -> Any: ...


def _load_base(
    parse_data_fn: Callable,
    datatype: DataType,
    source: Union[str, Path, os.PathLike, TextIOBase, BinaryIO],
    **kwargs,
) -> Any:
    input_mode, _, _ = _resolve_datatype(datatype)
    if isinstance(source, (str, Path, os.PathLike)):
        source = Path(source)
        with open(source, input_mode) as file:
            return parse_data_fn(file, **kwargs)
    else:
        return parse_data_fn(source, **kwargs)


@overload
def _loads_base(
    parse_data_fn: Callable,
    datatype: Literal["text"],
    source: str,
    /,
    **kwargs,
) -> Any: ...


@overload
def _loads_base(
    parse_data_fn: Callable,
    datatype: Literal["binary"],
    source: bytes,
    /,
    **kwargs,
) -> Any: ...


def _loads_base(
    parse_data_fn: Callable,
    datatype: DataType,
    source: Union[str, bytes],
    /,
    **kwargs,
) -> Any:
    _, _, buffer_type = _resolve_datatype(datatype)
    with buffer_type(source) as buffer:  # type: ignore
        return parse_data_fn(buffer, **kwargs)
