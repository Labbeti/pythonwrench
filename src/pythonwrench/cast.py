#!/usr/bin/env python
# -*- coding: utf-8 -*-

from argparse import Namespace
from dataclasses import asdict
from enum import Enum
from functools import partial
from pathlib import Path
from re import Pattern
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, TypeVar, overload

from pythonwrench._core import ClassOrTuple, Predicate, _FunctionRegistry
from pythonwrench.functools import identity
from pythonwrench.typing import (
    DataclassInstance,
    NamedTupleInstance,
    T_BuiltinScalar,
    is_builtin_scalar,
)

__all__ = ["register_as_builtin_fn", "as_builtin"]


K = TypeVar("K")
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
    ```
    >>> import numpy as np

    >>> @register_as_builtin_fn(np.ndarray)
    >>> def my_checksum_for_numpy(x: np.ndarray):
    >>>     return x.tolist()

    >>> pw.as_builtin([np.array([1, 2]), [3, 4]])
    ... [[1, 2], [3, 4]]
    ```
    """
    return _AS_BUILTIN_REGISTRY.register_decorator(
        class_or_tuple,
        custom_predicate=custom_predicate,
        priority=priority,
    )


_AS_BUILTIN_REGISTRY.register(
    identity, custom_predicate=partial(is_builtin_scalar, strict=True)
)


@register_as_builtin_fn(Path)
def _path_to_builtin(x: Path) -> str:
    return str(x)


@register_as_builtin_fn(Enum)
def _enum_to_builtin(x: Enum) -> str:
    return x.name


@register_as_builtin_fn(Pattern)
def _pattern_to_builtin(x: Pattern) -> str:
    return x.pattern


@register_as_builtin_fn(Namespace)
def _namespace_to_builtin(x: Namespace) -> Any:
    return as_builtin(x.__dict__)


@register_as_builtin_fn(DataclassInstance)
def _dataclass_to_builtin(x: DataclassInstance) -> Any:
    return as_builtin(asdict(x))


@register_as_builtin_fn(NamedTupleInstance)
def _namedtuple_to_builtin(x: NamedTupleInstance) -> Any:
    return as_builtin(x._asdict())


@register_as_builtin_fn(Mapping, priority=-100)
def _mapping_to_builtin(x: Mapping) -> Any:
    return {as_builtin(k): as_builtin(v) for k, v in x.items()}


@register_as_builtin_fn(Iterable, priority=-100)
def _iterable_to_builtin(x: Iterable) -> Any:
    return [as_builtin(xi) for xi in x]


@overload
def as_builtin(x: Enum) -> str: ...


@overload
def as_builtin(x: Path) -> str: ...


@overload
def as_builtin(x: Pattern) -> str: ...


@overload
def as_builtin(x: Namespace) -> Dict[str, Any]: ...


@overload
def as_builtin(x: Mapping[K, V]) -> Dict[K, V]: ...


@overload
def as_builtin(x: DataclassInstance) -> Dict[str, Any]: ...


@overload
def as_builtin(x: NamedTupleInstance) -> Dict[str, Any]: ...


@overload
def as_builtin(x: T_BuiltinScalar) -> T_BuiltinScalar: ...


@overload
def as_builtin(x: Any) -> Any: ...


def as_builtin(x: Any) -> Any:
    """Convert an object to a python builtin equivalent.

    This function can be used to sanitize data before saving to a JSON, YAML or CSV file.

    Args:
        x: Object to convert to built-in equivalent.
    """
    return _AS_BUILTIN_REGISTRY.apply(x)
