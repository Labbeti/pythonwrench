#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
import logging
import sys
import typing
from collections.abc import Callable as _RuntimeCallable
from collections.abc import Iterable as _RuntimeIterable
from dataclasses import is_dataclass
from numbers import Integral
from types import FunctionType, MethodType
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    Literal,
    Mapping,
    Sequence,
    Tuple,
    Type,
    TypedDict,
    Union,
)

import typing_extensions
from typing_extensions import (
    NotRequired,
    ParamSpec,
    Required,
    TypeGuard,
    TypeIs,
    TypeVar,
    get_args,
    get_origin,
)

from pythonwrench.typing.classes import (
    BuiltinCollection,
    BuiltinNumber,
    BuiltinScalar,
    DataclassInstance,
    NamedTupleInstance,
    NoneType,
)

T = TypeVar("T")
P = ParamSpec("P")

logger = logging.getLogger(__name__)


def check_args_types(fn: Callable[P, T]) -> Callable[P, T]:
    """Decorator to check argument types before call to a function.

    Example
    -------
    >>> import pythonwrench as pw
    >>> @pw.check_args_types
    >>> def f(a: int, b: str) -> str:
    >>>     return a * b
    >>> f(1, "a")  # pass check
    >>> f(1, 2)  # raises TypeError from decorator
    """
    if not isinstance(fn, (FunctionType, MethodType)):
        msg = f"Invalid argument type {type(fn)}. (expected function or method)"
        raise TypeError(msg)

    parameters = inspect.signature(fn).parameters
    annotations = {k: v.annotation for k, v in parameters.items()}
    argnames = list(annotations.keys())

    def _wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        num_positional = len(args)
        given_kwargs = dict(zip(argnames[:num_positional], args))
        given_kwargs.update(kwargs)

        msgs = []
        for i, (k, v) in enumerate(given_kwargs.items()):
            if isinstance_generic(v, annotations[k]):
                continue

            if i < num_positional:
                msg = f" - invalid argument n°{i + 1} with value {v!r}; expected an instance of {annotations[k]}."
            else:
                msg = f" - invalid argument '{k}' with value {v!r}; expected an instance of {annotations[k]}."
            msgs.append(msg)

        if len(msgs) > 0:
            msgs = [
                f"{fn.__name__}() has {len(msgs)}/{len(given_kwargs)} invalid argument(s):",
            ] + msgs
            msg = "\n".join(msgs)
            raise TypeError(msg)

        result = fn(*args, **kwargs)
        return result

    return _wrapper


def isinstance_generic(
    obj: Any,
    class_or_tuple: Union[Type[T], None, Tuple[Type[T], ...], Any],
    *,
    check_only_first: bool = False,
) -> TypeIs[T]:
    """Improved isinstance(...) function that supports parametrized Union, TypedDict, Literal, Mapping or Iterable.

    Args:
        obj: Object to check.
        class_or_tuple: Type to check. Can be a parametrized type from `typing`.
        check_only_first: If True, check only if first element when checking for Iterable[type]. defaults to False.

    Example 1
    ---------
    >>> isinstance_generic({"a": 1, "b": 2}, dict)
    ... True
    >>> isinstance_generic({"a": 1, "b": 2}, dict[str, int])
    ... True
    >>> isinstance_generic({"a": 1, "b": 2}, dict[str, str])
    ... False
    >>> from typing import Literal
    >>> isinstance_generic({"a": 1, "b": 2}, dict[str, Literal[1, 2]])
    ... True

    """
    if class_or_tuple is Any or class_or_tuple is typing_extensions.Any:
        return True
    if class_or_tuple is None:
        return obj is None
    if isinstance(class_or_tuple, tuple):
        return any(
            isinstance_generic(obj, target_type_i) for target_type_i in class_or_tuple
        )

    if is_typed_dict(class_or_tuple):
        return _isinstance_generic_typed_dict(obj, class_or_tuple)

    origin = get_origin(class_or_tuple)
    if origin is None:
        return isinstance(obj, class_or_tuple)  # type: ignore

    # Special case for empty tuple because get_args(Tuple[()]) returns () and not ((),) in python >= 3.11
    # More info at https://github.com/python/cpython/issues/91137
    if class_or_tuple == Tuple[()]:
        return obj == ()

    args = get_args(class_or_tuple)

    if _is_callable_type(origin):
        if not callable(obj):
            return False
        if len(args) == 0:
            return True
        elif len(args) != 2:
            msg = f"Invalid number of parameters in Callable. (found {len(args)} but expected 0 or 2)"
            raise RuntimeError(msg)

        sign = inspect.signature(obj)
        type_params_annots, type_return_annot = args
        obj_return_annot = sign.return_annotation

        if obj_return_annot != type_return_annot:
            return False

        obj_params_annots = [param.annotation for param in sign.parameters.values()]
        if type_params_annots is ...:
            return True

        if len(obj_params_annots) != len(type_params_annots):
            return False

        for obj_param_annot, type_param_annot in zip(
            obj_params_annots, type_params_annots
        ):
            if obj_param_annot != type_param_annot:
                return False

        return True

    if len(args) == 0:
        return isinstance_generic(obj, origin)

    if origin is Union:
        return any(isinstance_generic(obj, arg) for arg in args)

    if origin is Literal:
        return obj in args

    if isinstance(obj, Generator):
        msg = f"Invalid argument type {type(obj)}. (cannot check elements in generator)"
        raise TypeError(msg)

    if issubclass(origin, Generator):
        msg = f"Invalid argument type {origin}. (cannot check generator type)"
        raise TypeError(msg)

    if issubclass(origin, Mapping):
        assert len(args) == 2, f"{args=}"
        if not isinstance_generic(obj, origin):
            return False

        return all(isinstance_generic(k, args[0]) for k in obj.keys()) and all(
            isinstance_generic(v, args[1]) for v in obj.values()
        )

    if issubclass(origin, Tuple):
        if not isinstance_generic(obj, origin):
            return False
        elif len(args) == 1 and args[0] == ():
            return len(obj) == 0
        elif len(args) == 2 and args[1] is ...:
            if check_only_first:
                args = (args[0],)
            else:
                args = tuple([args[0]] * len(obj))
        elif len(obj) != len(args):
            return False
        return all(isinstance_generic(xi, ti) for xi, ti in zip(obj, args))

    if issubclass(origin, Iterable):
        if not isinstance_generic(obj, origin):
            return False

        if check_only_first:
            try:
                return isinstance_generic(next(iter(obj)), args[0])
            except StopIteration:
                return True
        else:
            return all(isinstance_generic(xi, args[0]) for xi in obj)

    msg = f"Unsupported type {class_or_tuple}. (expected unparametrized type or parametrized Union, TypedDict, Literal, Mapping or Iterable)"
    raise NotImplementedError(msg)


def _isinstance_generic_typed_dict(x: Any, target_type: type) -> bool:
    if not isinstance_generic(x, Dict[str, Any]):
        return False

    total: bool = target_type.__total__
    annotations = target_type.__annotations__

    required_annotations = {}
    optional_annotations = {}
    for k, v in annotations.items():
        origin = get_origin(v)
        if origin is Required:
            required_annotations[k] = v
        elif origin is NotRequired:
            optional_annotations[k] = v
        elif total:
            required_annotations[k] = v
        else:
            optional_annotations[k] = v

    if not set(required_annotations.keys()).issubset(x.keys()):
        return False

    annotations_set = set(required_annotations.keys()) | set(
        optional_annotations.keys()
    )
    if not annotations_set.issuperset(x.keys()):
        return False

    for k, v in required_annotations.items():
        origin = get_origin(v)
        if origin is Required:
            v = get_args(v)[0]

        if not isinstance_generic(x[k], v):
            return False

    for k, v in optional_annotations.items():
        if k not in x:
            continue
        origin = get_origin(v)
        if origin is NotRequired:
            v = get_args(v)[0]
        if not isinstance_generic(x[k], v):
            return False

    return True


def is_builtin_collection(x: Any, *, strict: bool = False) -> TypeIs[BuiltinCollection]:
    """Returns True if x is an instance of a builtin collection type (list, tuple, dict, set, frozenset).

    Args:
        x: Object to check.
        strict: If True, it will not consider custom subtypes of builtins as builtin collections. defaults to False.
    """
    if strict and not is_builtin_obj(x):
        return False
    return isinstance(x, (list, tuple, dict, set, frozenset))


def is_builtin_number(x: Any, *, strict: bool = False) -> TypeIs[BuiltinNumber]:
    """Returns True if x is an instance of a builtin number type (int, float, bool, complex).

    Args:
        x: Object to check.
        strict: If True, it will not consider custom subtypes of builtins as builtin numbers. defaults to False.
    """
    if strict and not is_builtin_obj(x):
        return False
    return isinstance(x, (int, float, bool, complex))


def is_builtin_obj(x: Any) -> bool:
    """Returns True if object is an instance of a builtin object.

    Note: If the object is an instance of a custom subtype of a builtin object, this function returns False.
    """
    return x.__class__.__module__ == "builtins" and not isinstance(x, type)


def is_builtin_scalar(x: Any, *, strict: bool = False) -> TypeIs[BuiltinScalar]:
    """Returns True if x is an instance of a builtin scalar type (int, float, bool, complex, NoneType, str, bytes).

    Args:
        x: Object to check.
        strict: If True, it will not consider subtypes of builtins as builtin scalars. defaults to False.
    """
    if strict and not is_builtin_obj(x):
        return False
    return isinstance(x, (int, float, bool, complex, NoneType, str, bytes))


def is_dataclass_instance(x: Any) -> TypeIs[DataclassInstance]:
    """Returns True if argument is a dataclass.

    Unlike function `dataclasses.is_dataclass`, this function returns False for a dataclass type.
    """
    return not isinstance(x, type) and isinstance_generic(x, DataclassInstance)


def is_dataclass_type(x: Any) -> TypeIs[Type[DataclassInstance]]:
    return isinstance(x, type) and is_dataclass(x)


def is_iterable_bool(
    x: Any,
    *,
    accept_generator: bool = True,
) -> TypeIs[Iterable[bool]]:
    if not accept_generator and isinstance(x, Generator):
        return False
    return isinstance_generic(x, Iterable[bool])


def is_iterable_bytes_or_list(
    x: Any,
    *,
    accept_generator: bool = True,
) -> TypeIs[Iterable[Union[bytes, list]]]:
    if not accept_generator and isinstance(x, Generator):
        return False
    return isinstance_generic(x, Iterable[Union[bytes, list]])


def is_iterable_float(
    x: Any,
    *,
    accept_generator: bool = True,
) -> TypeIs[Iterable[float]]:
    if not accept_generator and isinstance(x, Generator):
        return False
    return isinstance_generic(x, Iterable[float])


def is_iterable_int(
    x: Any,
    *,
    accept_bool: bool = True,
    accept_generator: bool = True,
) -> TypeIs[Iterable[int]]:
    if not accept_generator and isinstance(x, Generator):
        return False
    return isinstance_generic(x, Iterable[int]) and (
        accept_bool or not isinstance_generic(x, Iterable[bool])
    )


def is_iterable_integral(
    x: Any,
    *,
    accept_generator: bool = True,
) -> TypeIs[Iterable[Integral]]:
    if not accept_generator and isinstance(x, Generator):
        return False
    return isinstance_generic(x, Iterable[Integral])


def is_iterable_str(
    x: Any,
    *,
    accept_str: bool = True,
    accept_generator: bool = True,
) -> TypeGuard[Iterable[str]]:
    if isinstance(x, str):
        return accept_str
    if isinstance(x, Generator):
        return accept_generator and all(isinstance(xi, str) for xi in x)
    return isinstance_generic(x, Iterable[str])


def is_namedtuple_instance(x: Any) -> TypeIs[NamedTupleInstance]:
    """Returns True if argument is a NamedTuple."""
    return not isinstance(x, type) and isinstance_generic(x, NamedTupleInstance)


def is_sequence_str(
    x: Any,
    *,
    accept_str: bool = True,
) -> TypeGuard[Sequence[str]]:
    return (accept_str and isinstance(x, str)) or (
        not isinstance(x, str)
        and isinstance(x, Sequence)
        and all(isinstance(xi, str) for xi in x)
    )


def is_typed_dict(x: Any) -> TypeGuard[type]:
    if sys.version_info.major == 3 and sys.version_info.minor < 9:
        return x.__class__.__name__ == "_TypedDictMeta"
    else:
        return hasattr(x, "__orig_bases__") and TypedDict in x.__orig_bases__


def is_parameterized(x: Any) -> bool:
    """Returns True if object is a parametrized object like `Iterable[int]`, `Mapping[str, float]`, etc."""
    return get_origin(x) is not None and len(get_args(x)) > 0


_COLLECTION_ALIASES = [
    typing.Iterable,
    typing.Iterator,
    typing.Reversible,
    typing.Generator,
    typing.AsyncIterable,
    typing.AsyncIterator,
    typing.AsyncGenerator,
    typing.Collection,
    typing.Container,
    typing.Sized,
    typing.Sequence,
    typing.MutableSequence,
    typing.Set,
    typing.MutableSet,
    typing.Mapping,
    typing.MutableMapping,
    typing.MappingView,
    typing.KeysView,
    typing.ItemsView,
    typing.ValuesView,
    typing.Awaitable,
    typing.Coroutine,
    typing.Callable,
    typing.Hashable,
    typing_extensions.Iterable,
    typing_extensions.Iterator,
    typing_extensions.Reversible,
    typing_extensions.Generator,
    typing_extensions.AsyncIterable,
    typing_extensions.AsyncIterator,
    typing_extensions.AsyncGenerator,
    typing_extensions.Collection,
    typing_extensions.Container,
    typing_extensions.Sized,
    typing_extensions.Sequence,
    typing_extensions.MutableSequence,
    typing_extensions.Set,
    typing_extensions.MutableSet,
    typing_extensions.Mapping,
    typing_extensions.MutableMapping,
    typing_extensions.MappingView,
    typing_extensions.KeysView,
    typing_extensions.ItemsView,
    typing_extensions.ValuesView,
    typing_extensions.Awaitable,
    typing_extensions.Coroutine,
    typing_extensions.Callable,
    typing_extensions.Hashable,
]

_SPECIAL_FORMS = [] + [
    getattr(module, candidate_name, None)
    for module in (typing, typing_extensions)
    for candidate_name in [
        "Any",
        "NoReturn",
        "Union",
        "Optional",
        "Literal",
        "Final",
        "ClassVar",
        "TypeVar",
        "Annotated",
        "Never",
        "Self",
        "Required",
        "NotRequired",
        "TypeGuard",
        "TypeIs",
        "Concatenate",
        "ParamSpec",
        "ParamSpecArgs",
        "ParamSpecKwargs",
        "TypeVarTuple",
        "Unpack",
    ]
    if getattr(module, candidate_name, None) is not None
]


def is_collection_alias(x: Any) -> bool:
    """Returns True if object is a non-parameterized collection alias type."""
    return _safe_isin(x, _COLLECTION_ALIASES)


def is_special_form(x: Any) -> bool:
    """Returns True if object is a typing special form like `Any`."""
    return _safe_isin(x, _SPECIAL_FORMS)


def _safe_isin(x: Any, targets: Iterable) -> bool:
    for alias in targets:
        if (x == alias) is True:
            return True
    return False


def _is_callable_type(x: Any) -> bool:
    return x in (Callable, _RuntimeCallable)


def _is_iterable_type_like(x: Any) -> bool:
    return any(xi in (list, Iterable, _RuntimeIterable) for xi in (x, get_origin(x)))


def _is_literal_type(x: Any) -> bool:
    origin = get_origin(x)
    return origin is Literal


def _is_optional_type(x: Any) -> bool:
    return getattr(x, "__name__", None) == "Optional"


def _is_union_type(x: Any) -> bool:
    origin = get_origin(x)
    return origin == Union or getattr(origin, "__name__", None) in (
        "Union",
        "UnionType",
    )
