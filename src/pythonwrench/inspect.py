#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
from types import CodeType
from typing import Any, Callable, List, Tuple, TypeVar, Union, get_args

T = TypeVar("T")


def get_argnames(fn: Callable) -> List[str]:
    """Get arguments names of a method, function or callable object. This function does not return the 'self' argument for methods."""
    spec = inspect.getfullargspec(fn)
    all_args = spec.args + spec.kwonlyargs
    if inspect.ismethod(fn) or inspect.isclass(fn):
        return all_args[1:]
    else:
        return all_args


def get_current_fn_name(*, default: T = "") -> Union[str, T]:
    """Get caller function name."""
    try:
        return inspect.currentframe().f_back.f_code.co_name  # type: ignore
    except AttributeError:
        return default


def get_fullname(x: Any, *, inst_suffix: str = "(...)") -> str:
    """Returns the classname of an object with parent modules.

    Args:
        obj: Object to scan.
        inst_suffix: Suffix appended to the classname in case the object is an instance of a class.

    Examples
    --------
    >>> get_fullname([0, 1, 2])
    ... 'builtins.list(...)'
    >>> get_fullname(1.0)
    ... 'builtins.float(...)'
    >>> class A: def f(self): return 0
    >>> a = A()
    >>> get_fullname(a)
    ... '__main__.A(...)'
    >>> get_fullname(A)
    ... '__main__.A'
    >>> get_fullname(a.f)
    ... '__main__.A.f'
    >>> get_fullname(A.f)
    ... '__main__.A.f'
    """
    if hasattr(x, "__module__") and hasattr(x, "__qualname__"):
        if x.__module__ is None:
            name = f"{x.__qualname__}"
        else:
            name = f"{x.__module__}.{x.__qualname__}"
    elif inspect.ismodule(x):
        name = x.__name__
    else:
        cls = x.__class__
        name = f"{cls.__module__}.{cls.__qualname__}{inst_suffix}"

    cls_args = get_args(x)
    if len(cls_args) != 0:
        argsnames = [get_fullname(arg, inst_suffix=inst_suffix) for arg in cls_args]
        argsnames_str = ", ".join(argsnames)
        name = f"{name}[{argsnames_str}]"

    return name


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
