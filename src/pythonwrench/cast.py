#!/usr/bin/env python
# -*- coding: utf-8 -*-

from argparse import Namespace
from collections import Counter
from dataclasses import asdict
from datetime import date
from enum import Enum
from functools import partial
from pathlib import Path
from re import Pattern
from typing import (
    Any,
    Callable,
    Dict,
    Hashable,
    Iterable,
    Mapping,
    Optional,
    TypeVar,
    overload,
)

from pythonwrench._core import ClassOrTuple, Predicate, _FunctionRegistry
from pythonwrench.functools import identity
from pythonwrench.typing import (
    DataclassInstance,
    NamedTupleInstance,
    T_BuiltinScalar,
    is_builtin_scalar,
)

__all__ = ["register_as_builtin_fn", "as_builtin"]

T = TypeVar("T")
K = TypeVar("K", bound=Hashable)
V = TypeVar("V")

_AS_BUILTIN_REGISTRY = _FunctionRegistry[Any]()


@overload
def register_as_builtin_fn(
    class_or_tuple: ClassOrTuple,
    *,
    custom_predicate: None = None,
    priority: int = 0,
) -> Callable: ...


@overload
def register_as_builtin_fn(
    class_or_tuple: None = None,
    *,
    custom_predicate: Predicate,
    priority: int = 0,
) -> Callable: ...


def register_as_builtin_fn(
    class_or_tuple: Optional[ClassOrTuple] = None,
    *,
    custom_predicate: Optional[Predicate] = None,
    priority: int = 0,
) -> Callable:
    """Decorator to add an as_builtin function.

    Example
    -------
    >>> import numpy as np
    >>> @register_as_builtin_fn(np.ndarray)
    >>> def my_checksum_for_numpy(x: np.ndarray):
    >>>     return x.tolist()
    >>> pw.as_builtin([np.array([1, 2]), [3, 4]])
    ... [[1, 2], [3, 4]]
    """
    return _AS_BUILTIN_REGISTRY.register_decorator(
        class_or_tuple,
        custom_predicate=custom_predicate,
        priority=priority,
    )


_AS_BUILTIN_REGISTRY.register(
    identity,
    custom_predicate=partial(is_builtin_scalar, strict=True),
)


@register_as_builtin_fn(Counter)
def _counter_to_builtin(x: Counter, **kwargs) -> Dict[Any, int]:
    return dict(x)


@register_as_builtin_fn(date)
def _date_to_builtin(x: date, **kwargs) -> str:
    return str(x)


@register_as_builtin_fn(Path)
def _path_to_builtin(x: Path, **kwargs) -> str:
    return str(x)


@register_as_builtin_fn(Enum)
def _enum_to_builtin(x: Enum, **kwargs) -> str:
    return x.name


@register_as_builtin_fn(Pattern)
def _pattern_to_builtin(x: Pattern, **kwargs) -> str:
    return x.pattern


@register_as_builtin_fn(Namespace)
def _namespace_to_builtin(x: Namespace, **kwargs) -> Any:
    return as_builtin(x.__dict__, **kwargs)


@register_as_builtin_fn(DataclassInstance)
def _dataclass_to_builtin(x: DataclassInstance, **kwargs) -> Any:
    return as_builtin(asdict(x), **kwargs)


@register_as_builtin_fn(NamedTupleInstance)
def _namedtuple_to_builtin(x: NamedTupleInstance, **kwargs) -> Any:
    return as_builtin(x._asdict(), **kwargs)


@register_as_builtin_fn(Mapping, priority=-100)
def _mapping_to_builtin(x: Mapping, **kwargs) -> Any:
    return {as_builtin(k, **kwargs): as_builtin(v, **kwargs) for k, v in x.items()}


@register_as_builtin_fn(Iterable, priority=-200)
def _iterable_to_builtin(x: Iterable, **kwargs) -> Any:
    return [as_builtin(xi, **kwargs) for xi in x]


@overload
def as_builtin(x: Counter, **kwargs) -> Dict[Any, int]: ...


@overload
def as_builtin(x: date, **kwargs) -> str: ...


@overload
def as_builtin(x: Enum, **kwargs) -> str: ...


@overload
def as_builtin(x: Path, **kwargs) -> str: ...


@overload
def as_builtin(x: Pattern, **kwargs) -> str: ...


@overload
def as_builtin(x: Namespace, **kwargs) -> Dict[str, Any]: ...


@overload
def as_builtin(x: Mapping[K, V], **kwargs) -> Dict[K, V]: ...


@overload
def as_builtin(x: DataclassInstance, **kwargs) -> Dict[str, Any]: ...


@overload
def as_builtin(x: NamedTupleInstance, **kwargs) -> Dict[str, Any]: ...


@overload
def as_builtin(x: T_BuiltinScalar, **kwargs) -> T_BuiltinScalar: ...


@overload
def as_builtin(x: Any, **kwargs) -> Any: ...


def as_builtin(x: Any, **kwargs) -> Any:
    """Convert an object to a sanitized python builtin equivalent.

    This function can be used to sanitize data before saving to a JSON, YAML or CSV file.

    Additional objects to convert can be added dynamically with `pythonwrench.register_as_builtin_fn` function decorator.

    Here is the list of default objects converted to built-in:
    - tuple -> list
    - collections.Counter -> dict
    - datetime.date -> str
    - argparse.Namespace -> dict
    - re.Pattern -> str
    - pathlib.Path -> str
    - enum.Enum -> str
    - Mapping -> dict
    - Iterable -> list
    - Dataclass -> dict
    - NamedTuple -> dict

    Note: By default, tuple objects are converted to list.

    Args:
        x: Object to convert to built-in equivalent.
    """
    return _AS_BUILTIN_REGISTRY.apply(x, **kwargs)
