#!/usr/bin/env python
# -*- coding: utf-8 -*-

import functools
import re
import struct
import zlib
from dataclasses import asdict
from datetime import date, datetime
from enum import Enum
from functools import lru_cache
from pathlib import Path
from types import FunctionType, MethodType
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    Mapping,
    Optional,
    TypeVar,
    Union,
    get_args,
    get_origin,
    overload,
)

from pythonwrench._core import ClassOrTuple, Predicate, _FunctionRegistry
from pythonwrench.functools import function_alias
from pythonwrench.inspect import get_fullname
from pythonwrench.typing import (
    DataclassInstance,
    EllipsisType,
    NamedTupleInstance,
    NoneType,
    is_collection_alias,
    is_parameterized,
    is_special_form,
)

T = TypeVar("T")


_CHECKSUM_REGISTRY = _FunctionRegistry[int]()
_CHECKSUM_PROTOCOLS = False


@overload
def register_checksum_fn(
    class_or_tuple: ClassOrTuple,
    *,
    custom_predicate: None = None,
    priority: int = 0,
) -> Callable:
    """Perform the register checksum fn operation."""
    ...


@overload
def register_checksum_fn(
    class_or_tuple: None = None,
    *,
    custom_predicate: Predicate,
    priority: int = 0,
) -> Callable:
    """Perform the register checksum fn operation."""
    ...


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
    Not meant for security/cryptography.
    """
    return _CHECKSUM_REGISTRY.apply(x, isinstance_fn=isinstance_fn, **kwargs)


@function_alias(checksum_any)
def checksum_object(*args, **kwargs):
    """Return a checksum for object."""
    ...


# Terminate functions
@register_checksum_fn(bool)
def checksum_bool(x: bool, **kwargs) -> int:
    """Return a checksum for bool."""
    xint = int(x)
    return _terminate_checksum(
        xint,
        get_fullname(x),
        **kwargs,
    )


@register_checksum_fn(float)
def checksum_float(x: float, **kwargs) -> int:
    """Return a checksum for float."""
    xint = __interpret_float_as_int(x)
    return _terminate_checksum(
        xint,
        get_fullname(x),
        **kwargs,
    )


@register_checksum_fn(int)
def checksum_int(x: int, **kwargs) -> int:
    """Return a checksum for int."""
    xint = x
    return _terminate_checksum(
        xint,
        get_fullname(x),
        **kwargs,
    )


# Intermediate functions
@register_checksum_fn(bytearray)
def checksum_bytearray(x: bytearray, **kwargs) -> int:
    """Return a checksum for bytearray."""
    kwargs = _add_type_checksum_to_accumulator(x, kwargs)
    return _checksum_bytes_bytearray(x, **kwargs)


@register_checksum_fn(bytes)
def checksum_bytes(x: bytes, **kwargs) -> int:
    """Return a checksum for bytes."""
    return _checksum_bytes_bytearray(x, **kwargs)


@register_checksum_fn(complex)
def checksum_complex(x: complex, **kwargs) -> int:
    """Return a checksum for complex."""
    kwargs["accumulator"] = kwargs.get("accumulator", 0) + _cached_checksum_str(
        get_fullname(x)
    )
    return checksum_list_tuple([x.real, x.imag], **kwargs)


@register_checksum_fn(FunctionType)
def checksum_function(x: FunctionType, **kwargs) -> int:
    """Return a checksum for function."""
    kwargs = _add_type_checksum_to_accumulator(x, kwargs)
    return checksum_str(x.__qualname__, **kwargs)


@register_checksum_fn(NoneType)
def checksum_none(x: None, **kwargs) -> int:
    """Return a checksum for none."""
    kwargs = _add_type_checksum_to_accumulator(x, kwargs)
    return checksum_type(x.__class__, **kwargs)


@register_checksum_fn(EllipsisType)
def checksum_ellipsis(x: None, **kwargs) -> int:
    """Return a checksum for ellipsis."""
    kwargs = _add_type_checksum_to_accumulator(x, kwargs)
    return checksum_type(x.__class__, **kwargs)


@register_checksum_fn(str)
def checksum_str(x: str, **kwargs) -> int:
    """Return a checksum for str."""
    kwargs = _add_type_checksum_to_accumulator(x, kwargs)
    return checksum_bytes(x.encode(), **kwargs)


@register_checksum_fn(type)
def checksum_type(x: type, **kwargs) -> int:
    """Return a checksum for type."""
    return checksum_str(x.__qualname__, **kwargs)


# Recursive functions
@register_checksum_fn(DataclassInstance)
def checksum_dataclass(x: DataclassInstance, **kwargs) -> int:
    """Return a checksum for dataclass."""
    kwargs = _add_type_checksum_to_accumulator(x, kwargs)
    return checksum_dict(asdict(x), **kwargs)


@register_checksum_fn(datetime)
def checksum_datetime(x: datetime, **kwargs) -> int:
    """Return a checksum for datetime."""
    kwargs = _add_type_checksum_to_accumulator(x, kwargs)
    return _checksum_iterable(
        [
            x.year,
            x.month,
            x.day,
            x.hour,
            x.minute,
            x.second,
            x.microsecond,
            x.tzinfo,
            x.fold,
        ],
        **kwargs,
    )


@register_checksum_fn(date)
def checksum_date(x: date, **kwargs) -> int:
    """Return a checksum for date."""
    kwargs = _add_type_checksum_to_accumulator(x, kwargs)
    return _checksum_iterable([x.year, x.month, x.day], **kwargs)


@register_checksum_fn(dict)
def checksum_dict(x: dict, **kwargs) -> int:
    """Return a checksum for dict."""
    return _checksum_mapping(x, **kwargs)


@register_checksum_fn(Enum)
def checksum_enum(x: Enum, **kwargs) -> int:
    """Return a checksum for enum."""
    kwargs = _add_type_checksum_to_accumulator(x, kwargs)
    return _checksum_iterable((x.name, x.value), **kwargs)


@register_checksum_fn((list, tuple))
def checksum_list_tuple(x: Union[list, tuple], **kwargs) -> int:
    """Return a checksum for list tuple."""
    kwargs = _add_type_checksum_to_accumulator(x, kwargs)
    return _checksum_iterable(x, **kwargs)


@register_checksum_fn((set, frozenset))
def checksum_set(x: Union[set, frozenset], **kwargs) -> int:
    """Return a checksum for set."""
    kwargs = _add_type_checksum_to_accumulator(x, kwargs)
    # Simply use sum here, order does not matter
    csum = sum(checksum_any(xi, **kwargs) for xi in x)
    return csum


@register_checksum_fn(range)
def checksum_range(x: range, **kwargs) -> int:
    """Return a checksum for range."""
    kwargs = _add_type_checksum_to_accumulator(x, kwargs)
    return _checksum_iterable([x.start, x.stop, x.step], **kwargs)


@register_checksum_fn(Generator, priority=100)
def checksum_generator(x: Generator, **kwargs) -> int:
    """Return a checksum for generator."""
    msg = f"Cannot compute checksum for the generator object {type(x)=}, it will be consumed."
    raise RuntimeError(msg)


@register_checksum_fn(MethodType)
def checksum_method(x: MethodType, **kwargs) -> int:
    """Return a checksum for method."""
    fn = getattr(x.__self__, x.__name__)
    checksums = [
        checksum_any(x.__self__, **kwargs),  # type: ignore
        checksum_function(fn, **kwargs),
    ]
    return checksum_list_tuple(checksums, **kwargs)


@register_checksum_fn(NamedTupleInstance)
def checksum_namedtuple(x: NamedTupleInstance, **kwargs) -> int:
    """Return a checksum for namedtuple."""
    kwargs = _add_type_checksum_to_accumulator(x, kwargs)
    return checksum_dict(x._asdict(), **kwargs)


@register_checksum_fn(functools.partial)
def checksum_partial(x: functools.partial, **kwargs) -> int:
    """Return a checksum for partial."""
    kwargs = _add_type_checksum_to_accumulator(x, kwargs)
    return checksum_list_tuple((x.func, x.args, x.keywords), **kwargs)


@register_checksum_fn(re.Pattern)
def checksum_pattern(x: re.Pattern, **kwargs) -> int:
    """Return a checksum for pattern."""
    kwargs = _add_type_checksum_to_accumulator(x, kwargs)
    return checksum_str(str(x), **kwargs)


@register_checksum_fn(Path)
def checksum_path(x: Path, **kwargs) -> int:
    """Return a checksum for path."""
    kwargs = _add_type_checksum_to_accumulator(x, kwargs)

    resolve_path = kwargs.get("resolve_path", False)
    if isinstance(resolve_path, bool) and resolve_path:
        x = x.expanduser().resolve()
    return checksum_str(str(x), **kwargs)


@register_checksum_fn(slice)
def checksum_slice(x: slice, **kwargs) -> int:
    """Return a checksum for slice."""
    kwargs = _add_type_checksum_to_accumulator(x, kwargs)
    return checksum_list_tuple((x.start, x.stop, x.step), **kwargs)


@register_checksum_fn(custom_predicate=is_parameterized)
def checksum_parametrized(x: Any, **kwargs) -> int:
    """Return a checksum for parametrized."""
    kwargs = _add_type_checksum_to_accumulator(x, kwargs)
    return checksum_list_tuple((get_origin(x),) + get_args(x), **kwargs)


@register_checksum_fn(custom_predicate=is_collection_alias)
def checksum_collection_alias(x: Any, **kwargs) -> int:
    """Return a checksum for collection alias."""
    kwargs = _add_type_checksum_to_accumulator(x, kwargs)
    return checksum_str(x._name, **kwargs)


@register_checksum_fn(custom_predicate=is_special_form)
def checksum_special_form(x: Any, **kwargs) -> int:
    """Return a checksum for special form."""
    kwargs = _add_type_checksum_to_accumulator(x, kwargs)

    if hasattr(x, "_name"):
        name = x._name
    elif hasattr(x, "__name__"):
        name = x.__name__
    else:
        msg = f"Unsupported argument {x=} in checksum_special_form."
        raise ValueError(msg)

    return checksum_str(name, **kwargs)


if _CHECKSUM_PROTOCOLS:

    @register_checksum_fn(Mapping, priority=-100)
    def checksum_mapping(x: Mapping, **kwargs) -> int:
        """Return a checksum for mapping."""
        return _checksum_mapping(x, **kwargs)

    @register_checksum_fn(Iterable, priority=-200)
    def checksum_iterable(x: Iterable, **kwargs) -> int:
        """Return a checksum for iterable."""
        return _checksum_iterable(x, **kwargs)


# Private functions
def _checksum_bytes_bytearray(x: Union[bytes, bytearray], **kwargs) -> int:
    """Perform the checksum bytes bytearray operation."""
    xint = zlib.crc32(x) % (1 << 32)
    return _terminate_checksum(
        xint,
        get_fullname(x),
        **kwargs,
    )


def _checksum_iterable(x: Iterable, **kwargs) -> int:
    """Perform the checksum iterable operation."""
    accumulator = kwargs.pop("accumulator", 0) + _cached_checksum_str(get_fullname(x))
    csum = sum(
        checksum_any(xi, accumulator=accumulator + (i + 1), **kwargs) * (i + 1)
        for i, xi in enumerate(x)
    )
    return csum + accumulator


def _checksum_mapping(x: Mapping, **kwargs) -> int:
    """Perform the checksum mapping operation."""
    kwargs["accumulator"] = kwargs.get("accumulator", 0) + _cached_checksum_str(
        get_fullname(x)
    )
    return _checksum_iterable(x.items(), **kwargs)


def _terminate_checksum(x: int, fullname: str, **kwargs) -> int:
    """Returns checksum for final value + name + accumulator."""
    return x + _cached_checksum_str(fullname) + kwargs.get("accumulator", 0)


def _add_type_checksum_to_accumulator(x: Any, kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Perform the add type checksum to accumulator operation."""
    kwargs["accumulator"] = kwargs.get("accumulator", 0) + _cached_checksum_str(
        get_fullname(x)
    )
    return kwargs


@lru_cache(maxsize=None)
def _cached_checksum_str(x: str) -> int:
    """Perform the cached checksum str operation."""
    return zlib.crc32(x.encode()) % (1 << 32)


def __interpret_float_as_int(x: float) -> int:
    """Perform the interpret float as int operation."""
    xbytes = struct.pack(">d", x)
    xint = struct.unpack(">q", xbytes)[0]
    return xint
