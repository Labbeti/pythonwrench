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
    Generator,
    Iterable,
    Mapping,
    Optional,
    TypeVar,
    Union,
    overload,
)

from pythonwrench._core import ClassOrTuple, Predicate, _FunctionRegistry
from pythonwrench.inspect import get_fullname
from pythonwrench.typing import (
    DataclassInstance,
    NamedTupleInstance,
    NoneType,
)

T = TypeVar("T")


_CHECKSUM_REGISTRY = _FunctionRegistry[int]()


@overload
def register_checksum_fn(
    class_or_tuple: ClassOrTuple,
    *,
    custom_predicate: None = None,
    priority: int = 0,
) -> Callable: ...


@overload
def register_checksum_fn(
    class_or_tuple: None = None,
    *,
    custom_predicate: Predicate,
    priority: int = 0,
) -> Callable: ...


def register_checksum_fn(
    class_or_tuple: Optional[ClassOrTuple] = None,
    *,
    custom_predicate: Optional[Predicate] = None,
    priority: int = 0,
) -> Callable:
    """Decorator to add a checksum function.

    Example
    -------
    >>> import numpy as np
    >>> @register_checksum_fn(np.ndarray)
    >>> def my_checksum_for_numpy(x: np.ndarray):
    >>>     return int(x.sum())
    >>> pw.checksum_any(np.array([1, 2]))  # calls my_checksum_for_numpy internally, even if array in nested inside a list, dict, etc.
    """
    return _CHECKSUM_REGISTRY.register_decorator(
        class_or_tuple,
        custom_predicate=custom_predicate,
        priority=priority,
    )


def checksum_any(
    x: Any,
    *,
    isinstance_fn: Callable[[Any, Union[type, tuple]], bool] = isinstance,
    **kwargs,
) -> int:
    """Compute checksum integer value from an arbitrary object.

    Supports most builtin types. Checksum can be used to compare objects.
    """
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
    # Simply use sum here, order does not matter
    csum = sum(checksum_any(xi, **kwargs) for xi in x)
    return csum


@register_checksum_fn(range)
def checksum_range(x: range, **kwargs) -> int:
    kwargs["accumulator"] = kwargs.get("accumulator", 0) + _cached_checksum_str(
        get_fullname(x)
    )
    return _checksum_iterable([x.start, x.stop, x.step], **kwargs)


@register_checksum_fn(Generator, priority=100)
def checksum_generator(x: Generator, **kwargs) -> int:
    msg = f"Cannot compute checksum for the generator object {type(x)=}, it will be consumed."
    raise RuntimeError(msg)


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
