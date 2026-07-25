#!/usr/bin/env python
# -*- coding: utf-8 -*-

import warnings
from functools import lru_cache, partial
from typing import Any, Callable, Optional, Type, TypeVar, Union, overload

from typing_extensions import ParamSpec

from pythonwrench._core import T_Function, _decorator_factory, return_none

P = ParamSpec("P")
U = TypeVar("U")


@overload
def warn_once(
    message: str,
    category: Optional[Type[Warning]] = None,
    stacklevel: int = 1,
    source: Any = None,
) -> None: ...


@overload
def warn_once(
    message: Warning,
    category: Any = None,
    stacklevel: int = 1,
    source: Any = None,
) -> None: ...


@lru_cache(maxsize=None)
def warn_once(
    message: Union[str, Warning],
    category: Optional[Type[Warning]] = None,
    stacklevel: int = 1,
    source: Any = None,
) -> None:
    """Warn message once using warnings module."""
    warnings.warn(message, category, stacklevel, source)


def deprecated_alias(
    alternative: T_Function,
    msg_fmt: str = "Deprecated call to '{fn_name}', use '{alternative_name}' instead.",
    warn_fn: Callable[[str], Any] = partial(warn_once, category=DeprecationWarning),
    *,
    pre_fn: Optional[Callable[..., Any]] = None,
    post_fn: Optional[Callable[..., Any]] = None,
) -> Callable[..., T_Function]:
    """Decorator to wrap deprecated function aliases."""
    alternative_name = alternative.__name__ if alternative is not None else "None"
    if pre_fn is None:
        pre_fn = return_none

    def inner_pre_fn(fn, *args, **kwargs) -> None:
        msg = msg_fmt.format(fn_name=fn.__name__, alternative_name=alternative_name)
        warn_fn(msg)
        pre_fn(fn, *args, **kwargs)

    return _decorator_factory(alternative, pre_fn=inner_pre_fn, post_fn=post_fn)


@overload
def deprecated_function(
    fn: None = None,
    /,
    *,
    msg_fmt: str = "Deprecated call to '{fn_name}'.",
    warn_fn: Callable[[str], Any] = partial(warn_once, category=DeprecationWarning),
) -> Callable[[T_Function], T_Function]: ...


@overload
def deprecated_function(
    fn: T_Function,
    /,
    *,
    msg_fmt: str = "Deprecated call to '{fn_name}'.",
    warn_fn: Callable[[str], Any] = partial(warn_once, category=DeprecationWarning),
) -> T_Function: ...


def deprecated_function(
    fn: Optional[T_Function] = None,
    /,
    *,
    msg_fmt: str = "Deprecated call to '{fn_name}'.",
    warn_fn: Callable[[str], Any] = partial(warn_once, category=DeprecationWarning),
    pre_fn: Optional[Callable[..., Any]] = None,
    post_fn: Optional[Callable[..., Any]] = None,
) -> Union[Callable[[T_Function], T_Function], T_Function]:
    """Decorator to wrap deprecated functions."""
    if pre_fn is None:
        pre_fn = return_none

    def inner_pre_fn(fn, *args, **kwargs):
        msg = msg_fmt.format(fn_name=fn.__qualname__)
        warn_fn(msg)
        pre_fn(fn, *args, **kwargs)

    decorator = _decorator_factory(None, pre_fn=inner_pre_fn, post_fn=post_fn)
    if fn is None:
        return decorator
    else:
        return decorator(fn)
