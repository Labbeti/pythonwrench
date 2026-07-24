#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
from types import CodeType
from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    Tuple,
    TypeVar,
    overload,
)

from typing_extensions import ParamSpec

from pythonwrench._core import _decorator_factory, return_none  # noqa: F401
from pythonwrench.inspect import get_argnames, get_fullname
from pythonwrench.typing import isinstance_generic

T = TypeVar("T")
P = ParamSpec("P")
U = TypeVar("U")


class Compose(Generic[T, U]):
    """Compose callables to chain calls sequentially."""

    @overload
    def __init__(self) -> None: ...

    @overload
    def __init__(
        self,
        fn0: Iterable[Callable[[T], T]],
        /,
    ) -> None: ...

    @overload
    def __init__(
        self,
        fn0: Callable[[T], U],
        /,
    ) -> None: ...

    @overload
    def __init__(
        self,
        fn0: Callable[[T], Any],
        fn1: Callable[[Any], U],
        /,
    ) -> None: ...

    @overload
    def __init__(
        self,
        fn0: Callable[[T], Any],
        fn1: Callable[[Any], Any],
        fn2: Callable[[Any], U],
        /,
    ) -> None: ...

    @overload
    def __init__(
        self,
        fn0: Callable[[T], Any],
        fn1: Callable[[Any], Any],
        fn2: Callable[[Any], Any],
        fn3: Callable[[Any], U],
        /,
    ) -> None: ...

    @overload
    def __init__(
        self,
        fn0: Callable[[T], Any],
        fn1: Callable[[Any], Any],
        fn2: Callable[[Any], Any],
        fn3: Callable[[Any], Any],
        fn4: Callable[[Any], U],
        /,
    ) -> None: ...

    @overload
    def __init__(self, *fns: Callable) -> None: ...

    def __init__(self, *fns) -> None:
        if isinstance_generic(fns, Tuple[Iterable[Callable]]):
            fns = fns[0]
        elif isinstance_generic(fns, Tuple[Callable, ...]):
            pass
        else:
            msg = f"Invalid argument types {type(fns)=}. (with {fns=})"
            raise TypeError(msg)

        super().__init__()
        self.fns = fns

    def __call__(self, x: T) -> U:
        for fn in self.fns:
            x = fn(x)
        return x  # type: ignore

    def __getitem__(self, idx: int, /) -> Callable[[Any], Any]:
        return self.fns[idx]

    def __len__(self) -> int:
        return len(self.fns)


compose = Compose  # type: ignore


def filter_and_call(
    fn: Callable[..., T], _fill_all_arguments: bool = False, **kwargs: Any
) -> T:
    """Call object only with the valid keyword arguments. Non-valid arguments are ignored.

    Arguments:
        fn: Callable to call.
        _fill_all_arguments: If True, all arguments of fn must be provided in kwargs. defaults to False.
        **kwargs: Superset of arguments to pass to fn.
            Name that does not match any argument of fn are ignored.

    Examples:
    ---------
    >>> def f(x, y):
    >>>     return x + y
    >>> filter_and_call(f, y=2, x=1)
    ... 3
    >>> filter_and_call(f, y=2, x=1, z=0)  # z is ignored
    ... 3
    """
    argnames = get_argnames(fn)
    code, _start = _get_code_and_start(fn)

    if "_fill_all_arguments" in argnames:
        msg = f"Invalid argument {get_fullname(fn)}, because it has argument '_fill_all_arguments'."
        raise RuntimeError(msg)

    if _fill_all_arguments:
        missing = set(argnames).difference(kwargs)
        if len(missing) > 0:
            msg = f"Missing {len(missing)}/{len(argnames)} arguments: {tuple(missing)}. (with {_fill_all_arguments=})"
            raise ValueError(msg)

    pos_argnames = argnames[: code.co_posonlyargcount]
    other_argnames = argnames[code.co_posonlyargcount :]

    posonly_args = {
        name: value for name, value in kwargs.items() if name in pos_argnames
    }
    other_kwds = {
        name: value for name, value in kwargs.items() if name in other_argnames
    }
    result = fn(*posonly_args.values(), **other_kwds)
    return result


def function_alias(alternative: Callable[P, U]) -> Callable[..., Callable[P, U]]:
    """Decorator to wrap function aliases.

    Example
    -------
    >>> def f(a: int, b: str) -> str:
    >>>    return a * b
    >>> @function_alias(f)
    >>> def g(*args, **kwargs): ...
    >>> f(2, "a")
    ... "aa"
    >>> g(3, "b")  # calls function f() internally.
    ... "bbb"

    """
    return _decorator_factory(alternative)


def identity(x: T, **kwargs) -> T:
    """Identity function placeholder. Returns the first argument. Other keywords arguments are ignored."""
    return x


def repeat_fn(f: Callable[[T], T], n: int) -> Callable[[T], T]:
    """Creates wrapper which call a function n items."""
    return Compose([f] * n)


def _get_code_and_start(fn: Callable) -> Tuple[CodeType, int]:
    if inspect.isfunction(fn):
        code = fn.__code__
        start = 0
    elif inspect.ismethod(fn):
        code = fn.__code__
        start = 1  # If method, remove 'self' arg
    elif inspect.isclass(fn):
        # If init, remove 'self' arg
        code = fn.__init__.__code__
        start = 1  # If init, remove 'self' arg
    else:
        code = fn.__call__.__code__
        start = 0

    return code, start
