#!/usr/bin/env python
# -*- coding: utf-8 -*-

import functools
import re
import struct
import zlib
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path
from types import FunctionType, MethodType
from typing import (
    Any,
    Callable,
    Iterable,
    Mapping,
    Optional,
    TypeVar,
    Union,
    get_args,
    overload,
)

from pythonwrench._core import ClassOrTuple, Predicate, _FunctionRegistry
from pythonwrench.inspect import get_fullname
from pythonwrench.typing import (
    BuiltinNumber,
    BuiltinScalar,
    DataclassInstance,
    NamedTupleInstance,
    NoneType,
    is_builtin_number,
    is_builtin_scalar,
)

T = TypeVar("T")


_CHECKSUM_REGISTRY = _FunctionRegistry[int]()


@overload
def register_checksum_fn(
    class_or_tuple: ClassOrTuple,
    *,
    custom_predicate: None = None,
) -> Callable: ...


@overload
def register_checksum_fn(
    class_or_tuple: None = None,
    *,
    custom_predicate: Predicate,
) -> Callable: ...


def register_checksum_fn(
    class_or_tuple: Optional[ClassOrTuple] = None,
    *,
    custom_predicate: Optional[Predicate] = None,
) -> Callable:
    """Decorator to add a checksum function.
    ```
    >>> import numpy as np

    >>> @register_checksum_fn(np.ndarray)
    >>> def my_checksum_for_numpy(x: np.ndarray):
    >>>     return int(x.sum())

    >>> pw.checksum_any(np.array([1, 2]))  # calls my_checksum_for_numpy internally, even if array in nested inside a list, dict, etc.
    ```
    """
    return _CHECKSUM_REGISTRY.register_decorator(
        class_or_tuple,
        custom_predicate=custom_predicate,
    )


def checksum_any(
    x: Any,
    *,
    isinstance_fn: Callable[[Any, Union[type, tuple]], bool] = isinstance,
    **kwargs,
) -> int:
    return _CHECKSUM_REGISTRY.apply(x, isinstance_fn=isinstance_fn, **kwargs)


# Terminate functions
@register_checksum_fn(bool)
def checksum_bool(x: bool, **kwargs) -> int:
    xint = int(x)
    return _terminate_checksum(
        xint,
        get_fullname(x),
        **kwargs,
    )


@register_checksum_fn(float)
def checksum_float(x: float, **kwargs) -> int:
    xint = __interpret_float_as_int(x)
    return _terminate_checksum(
        xint,
        get_fullname(x),
        **kwargs,
    )


@register_checksum_fn(int)
def checksum_int(x: int, **kwargs) -> int:
    xint = x
    return _terminate_checksum(
        xint,
        get_fullname(x),
        **kwargs,
    )


# Intermediate functions
@register_checksum_fn(None, custom_predicate=is_builtin_scalar)
def checksum_builtin_scalar(x: BuiltinScalar, **kwargs) -> int:
    if is_builtin_number(x):
        return checksum_builtin_number(x, **kwargs)
    elif isinstance(x, bytes):
        return checksum_bytes(x, **kwargs)
    elif x is None:
        return checksum_none(x, **kwargs)
    elif isinstance(x, str):
        return checksum_str(x, **kwargs)
    else:
        msg = f"Invalid argument type {type(x)}. (expected one of {get_args(BuiltinScalar)})"
        raise TypeError(msg)


@register_checksum_fn(None, custom_predicate=is_builtin_number)
def checksum_builtin_number(x: BuiltinNumber, **kwargs) -> int:
    """Compute a simple checksum of a builtin scalar number."""
    # Note: instance check must follow this order: bool, int, float, complex, because isinstance(True, int) returns True !
    if isinstance(x, bool):
        return checksum_bool(x, **kwargs)
    elif isinstance(x, int):
        return checksum_int(x, **kwargs)
    elif isinstance(x, float):
        return checksum_float(x, **kwargs)
    elif isinstance(x, complex):
        return checksum_complex(x, **kwargs)
    else:
        msg = f"Invalid argument type {type(x)}. (expected one of {get_args(BuiltinNumber)})"
        raise TypeError(msg)


@register_checksum_fn(bytearray)
def checksum_bytearray(x: bytearray, **kwargs) -> int:
    kwargs["accumulator"] = kwargs.get("accumulator", 0) + _cached_checksum_str(
        get_fullname(x)
    )
    return _checksum_bytes_bytearray(x, **kwargs)


@register_checksum_fn(bytes)
def checksum_bytes(x: bytes, **kwargs) -> int:
    return _checksum_bytes_bytearray(x, **kwargs)


@register_checksum_fn(complex)
def checksum_complex(x: complex, **kwargs) -> int:
    kwargs["accumulator"] = kwargs.get("accumulator", 0) + _cached_checksum_str(
        get_fullname(x)
    )
    return checksum_list_tuple([x.real, x.imag], **kwargs)


@register_checksum_fn(FunctionType)
def checksum_function(x: FunctionType, **kwargs) -> int:
    kwargs["accumulator"] = kwargs.get("accumulator", 0) + _cached_checksum_str(
        get_fullname(x)
    )
    return checksum_str(x.__qualname__, **kwargs)


@register_checksum_fn(NoneType)
def checksum_none(x: None, **kwargs) -> int:
    kwargs["accumulator"] = kwargs.get("accumulator", 0) + _cached_checksum_str(
        get_fullname(x)
    )
    return checksum_type(x.__class__, **kwargs) + kwargs.get("accumulator", 0)


@register_checksum_fn(str)
def checksum_str(x: str, **kwargs) -> int:
    kwargs["accumulator"] = kwargs.get("accumulator", 0) + _cached_checksum_str(
        get_fullname(x)
    )
    return checksum_bytes(x.encode(), **kwargs)


@register_checksum_fn(type)
def checksum_type(x: type, **kwargs) -> int:
    return checksum_str(x.__qualname__, **kwargs)


# Recursive functions
@register_checksum_fn(DataclassInstance)
def checksum_dataclass(x: DataclassInstance, **kwargs) -> int:
    kwargs["accumulator"] = kwargs.get("accumulator", 0) + _cached_checksum_str(
        get_fullname(x)
    )
    return checksum_dict(asdict(x), **kwargs)


@register_checksum_fn(dict)
def checksum_dict(x: dict, **kwargs) -> int:
    return _checksum_mapping(x, **kwargs)


@register_checksum_fn((list, tuple))
def checksum_list_tuple(x: Union[list, tuple], **kwargs) -> int:
    return _checksum_iterable(x, **kwargs)


@register_checksum_fn((set, frozenset))
def checksum_set(x: Union[set, frozenset], **kwargs) -> int:
    kwargs["accumulator"] = kwargs.get("accumulator", 0) + _cached_checksum_str(
        get_fullname(x)
    )
    return _checksum_iterable(sorted(x), **kwargs)


@register_checksum_fn(range)
def checksum_range(x: range, **kwargs) -> int:
    kwargs["accumulator"] = kwargs.get("accumulator", 0) + _cached_checksum_str(
        get_fullname(x)
    )
    return _checksum_iterable([x.start, x.stop, x.step], **kwargs)


@register_checksum_fn(MethodType)
def checksum_method(x: MethodType, **kwargs) -> int:
    fn = getattr(x.__self__, x.__name__)
    checksums = [
        checksum_any(x.__self__, **kwargs),  # type: ignore
        checksum_function(fn, **kwargs),
    ]
    return checksum_list_tuple(checksums, **kwargs)


@register_checksum_fn(NamedTupleInstance)
def checksum_namedtuple(x: NamedTupleInstance, **kwargs) -> int:
    kwargs["accumulator"] = kwargs.get("accumulator", 0) + _cached_checksum_str(
        get_fullname(x)
    )
    return checksum_dict(x._asdict(), **kwargs)


@register_checksum_fn(functools.partial)
def checksum_partial(x: functools.partial, **kwargs) -> int:
    kwargs["accumulator"] = kwargs.get("accumulator", 0) + _cached_checksum_str(
        get_fullname(x)
    )
    return checksum_list_tuple((x.func, x.args, x.keywords), **kwargs)


@register_checksum_fn(re.Pattern)
def checksum_pattern(x: re.Pattern, **kwargs) -> int:
    kwargs["accumulator"] = kwargs.get("accumulator", 0) + _cached_checksum_str(
        get_fullname(x)
    )
    return checksum_str(str(x), **kwargs)


@register_checksum_fn(Path)
def checksum_path(x: Path, **kwargs) -> int:
    kwargs["accumulator"] = kwargs.get("accumulator", 0) + _cached_checksum_str(
        get_fullname(x)
    )
    return checksum_str(str(x), **kwargs)


@register_checksum_fn(slice)
def checksum_slice(x: slice, **kwargs) -> int:
    kwargs["accumulator"] = kwargs.get("accumulator", 0) + _cached_checksum_str(
        get_fullname(x)
    )
    return checksum_list_tuple((x.start, x.stop, x.step), **kwargs)


# Private functions
def _checksum_bytes_bytearray(x: Union[bytes, bytearray], **kwargs) -> int:
    xint = zlib.crc32(x) % (1 << 32)
    return _terminate_checksum(
        xint,
        get_fullname(x),
        **kwargs,
    )


def _checksum_iterable(x: Iterable, **kwargs) -> int:
    accumulator = kwargs.pop("accumulator", 0) + _cached_checksum_str(get_fullname(x))
    csum = sum(
        checksum_any(xi, accumulator=accumulator + (i + 1), **kwargs) * (i + 1)
        for i, xi in enumerate(x)
    )
    return csum + accumulator


def _checksum_mapping(x: Mapping, **kwargs) -> int:
    kwargs["accumulator"] = kwargs.get("accumulator", 0) + _cached_checksum_str(
        get_fullname(x)
    )
    return _checksum_iterable(x.items(), **kwargs)


def _terminate_checksum(x: int, fullname: str, **kwargs) -> int:
    return x + _cached_checksum_str(fullname) + kwargs.get("accumulator", 0)


@lru_cache(maxsize=None)
def _cached_checksum_str(x: str) -> int:
    return zlib.crc32(x.encode()) % (1 << 32)


def __interpret_float_as_int(x: float) -> int:
    xbytes = struct.pack(">d", x)
    xint = struct.unpack(">q", xbytes)[0]
    return xint
