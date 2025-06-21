#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import (
    Any,
    Callable,
    Iterable,
    Literal,
    Optional,
    TypeVar,
)

from pythonwrench.functools import function_alias

K = TypeVar("K", covariant=True)
T = TypeVar("T", covariant=True)
U = TypeVar("U", covariant=True)
V = TypeVar("V", covariant=True)
W = TypeVar("W", covariant=True)
X = TypeVar("X", covariant=True)
Y = TypeVar("Y", covariant=True)

KeyMode = Literal["intersect", "same", "union"]
Order = Literal["left", "right"]


def all_eq(it: Iterable[T], eq_fn: Optional[Callable[[T, T], bool]] = None) -> bool:
    """Returns true if all elements in iterable are equal.

    Note: This function returns True for iterable that contains 0 or 1 element.
    """
    it = list(it)
    try:
        first = next(iter(it))
    except StopIteration:
        return True

    if eq_fn is None:
        return all(first == elt for elt in it)
    else:
        return all(eq_fn(first, elt) for elt in it)


def all_ne(
    it: Iterable[T],
    ne_fn: Optional[Callable[[T, T], bool]] = None,
    use_set: bool = False,
) -> bool:
    """Returns true if all elements in iterable are differents.

    Note: This function returns True for iterable that contains 0 or 1 element.
    """
    if isinstance(it, (set, frozenset, dict)):
        return True
    if use_set and ne_fn is not None:
        raise ValueError(f"Cannot use arguments {use_set=} with {ne_fn=}.")

    it = list(it)
    if use_set:
        return len(it) == len(set(it))
    elif ne_fn is None:
        return all(
            it[i] != it[j] for i in range(len(it)) for j in range(i + 1, len(it))
        )
    else:
        return all(
            ne_fn(it[i], it[j]) for i in range(len(it)) for j in range(i + 1, len(it))
        )


@function_alias(all_eq)
def is_full(*args, **kwargs): ...


def is_sorted(
    x: Iterable[Any],
    *,
    reverse: bool = False,
    strict: bool = False,
) -> bool:
    it = iter(x)
    try:
        prev = next(it)
    except StopIteration:
        return True

    for xi in it:
        if not reverse and prev > xi:
            return False
        if reverse and prev < xi:
            return False
        if strict and prev == xi:
            return False
        prev = xi
    return True


@function_alias(all_ne)
def is_unique(*args, **kwargs): ...
