#!/usr/bin/env python
# -*- coding: utf-8 -*-

import operator
from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    Optional,
    Tuple,
    Type,
    TypeVar,
    overload,
)

from pythonwrench.functools import function_alias
from pythonwrench.typing.checks import isinstance_generic
from pythonwrench.typing.classes import (
    SupportsAdd,
    SupportsAnd,
    SupportsMul,
    SupportsOr,
)

T = TypeVar("T")
T_SupportsAdd = TypeVar("T_SupportsAdd", bound=SupportsAdd)
T_SupportsAnd = TypeVar("T_SupportsAnd", bound=SupportsAnd)
T_SupportsMul = TypeVar("T_SupportsMul", bound=SupportsMul)
T_SupportsOr = TypeVar("T_SupportsOr", bound=SupportsOr)


@overload
def reduce_add(
    args: Iterable[T_SupportsAdd],
    /,
    *,
    start: T_SupportsAdd,
) -> T_SupportsAdd: ...


@overload
def reduce_add(
    *args: T_SupportsAdd,
    start: T_SupportsAdd,
) -> T_SupportsAdd: ...


@overload
def reduce_add(
    arg0: T_SupportsAdd,
    /,
    *args: T_SupportsAdd,
    start: Optional[T_SupportsAdd] = None,
) -> T_SupportsAdd: ...


def reduce_add(*args, start=None):
    return _reduce(*args, start=start, op_fn=operator.add, type_=SupportsAdd)


@overload
def reduce_and(
    args: Iterable[T_SupportsAnd],
    /,
    *,
    start: T_SupportsAnd,
) -> T_SupportsAnd: ...


@overload
def reduce_and(
    *args: T_SupportsAnd,
    start: T_SupportsAnd,
) -> T_SupportsAnd: ...


@overload
def reduce_and(
    arg0: T_SupportsAnd,
    /,
    *args: T_SupportsAnd,
    start: Optional[T_SupportsAnd] = None,
) -> T_SupportsAnd: ...


def reduce_and(*args, start=None):
    return _reduce(*args, start=start, op_fn=operator.and_, type_=SupportsAnd)


@overload
def reduce_mul(
    args: Iterable[T_SupportsMul],
    /,
    *,
    start: T_SupportsMul,
) -> T_SupportsMul: ...


@overload
def reduce_mul(
    *args: T_SupportsMul,
    start: T_SupportsMul,
) -> T_SupportsMul: ...


@overload
def reduce_mul(
    arg0: T_SupportsMul,
    /,
    *args: T_SupportsMul,
    start: Optional[T_SupportsMul] = None,
) -> T_SupportsMul: ...


def reduce_mul(*args, start=None):
    return _reduce(*args, start=start, op_fn=operator.mul, type_=SupportsMul)


@overload
def reduce_or(
    args: Iterable[T_SupportsOr],
    /,
    *,
    start: T_SupportsOr,
) -> T_SupportsOr: ...


@overload
def reduce_or(
    *args: T_SupportsOr,
    start: T_SupportsOr,
) -> T_SupportsOr: ...


@overload
def reduce_or(
    arg0: T_SupportsOr,
    /,
    *args: T_SupportsOr,
    start: Optional[T_SupportsOr] = None,
) -> T_SupportsOr: ...


def reduce_or(*args, start=None):
    return _reduce(*args, start=start, op_fn=operator.or_, type_=SupportsOr)


def _reduce(
    *args,
    start: Optional[T] = None,
    op_fn: Callable[[T, T], T],
    type_: Type[T],
) -> T:
    if isinstance_generic(args, Tuple[Iterable[type_]]):
        it_or_args = args[0]
    elif isinstance_generic(args, Tuple[type_, ...]):
        it_or_args = args
    else:
        msg = f"Invalid positional arguments {args}. (expected {Tuple[type_, ...]} or {Tuple[Iterable[type_]]})"
        raise TypeError(msg)

    it: Iterator[T] = iter(it_or_args)

    if isinstance(start, type_):
        accumulator = start
    elif start is None:
        try:
            accumulator = next(it)
        except StopIteration:
            msg = f"Invalid combinaison of arguments {args=} and {start=}. (expected at least 1 non-empty argument or start that supports or operator.)"
            raise ValueError(msg)
    else:
        raise TypeError(f"Invalid argument type {type(start)}.")

    for arg in it:
        accumulator = op_fn(accumulator, arg)
    return accumulator


@overload
def sum(
    args: Iterable[T_SupportsAdd],
    /,
    *,
    start: T_SupportsAdd = 0,
) -> T_SupportsAdd: ...


@overload
def sum(
    *args: T_SupportsAdd,
    start: T_SupportsAdd = 0,
) -> T_SupportsAdd: ...


@overload
def sum(
    arg0: T_SupportsAdd,
    /,
    *args: T_SupportsAdd,
    start: Optional[T_SupportsAdd] = 0,
) -> T_SupportsAdd: ...


def sum(*args, start: Any = 0):
    return reduce_add(*args, start=start)


@overload
def prod(
    args: Iterable[T_SupportsMul],
    /,
    *,
    start: T_SupportsMul = 1,
) -> T_SupportsMul: ...


@overload
def prod(
    *args: T_SupportsMul,
    start: T_SupportsMul = 1,
) -> T_SupportsMul: ...


@overload
def prod(
    arg0: T_SupportsMul,
    /,
    *args: T_SupportsMul,
    start: Optional[T_SupportsMul] = 1,
) -> T_SupportsMul: ...


def prod(*args, start: Any = 1):
    return reduce_mul(*args, start=start)


@function_alias(reduce_and)
def intersect(*args, **kwargs): ...


@function_alias(reduce_or)
def union(*args, **kwargs): ...
