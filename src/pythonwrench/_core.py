#!/usr/bin/env python
# -*- coding: utf-8 -*-

import warnings
from functools import lru_cache, partial, wraps
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Literal,
    Optional,
    Protocol,
    Tuple,
    Type,
    Union,
    get_args,
    overload,
    runtime_checkable,
)

from typing_extensions import ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T", covariant=True)
U = TypeVar("U", covariant=True)

T_Output = TypeVar("T_Output", default=Any)
T_PredicateArg = TypeVar("T_PredicateArg", contravariant=True, default=Any)
T_Function = TypeVar("T_Function", bound=Callable[..., Any])

UnkMode = Literal["identity", "error"]
ClassOrTuple = Union[type, Tuple[type, ...]]


@runtime_checkable
class Predicate(Protocol[T_PredicateArg]):
    def __call__(self, /, x: T_PredicateArg) -> bool:
        """Call the instance."""
        ...


def return_none(*args, **kwargs) -> None:
    """Return None function placeholder."""
    return None


def function_alias(
    alternative: T_Function,
    *,
    pre_fn: Optional[Callable[..., Any]] = None,
    post_fn: Optional[Callable[..., Any]] = None,
) -> Callable[..., T_Function]:
    """Decorator to wrap function aliases.

    Unlike setting directly an alias, this preserve the nature of the alias for language server.

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
    return _decorator_factory(alternative, pre_fn=pre_fn, post_fn=post_fn)


def _decorator_factory(
    inner_fn: Optional[T_Function],
    *,
    pre_fn: Optional[Callable[..., Any]] = None,
    post_fn: Optional[Callable[..., Any]] = None,
) -> Callable[[T_Function], T_Function]:
    """Decorator for function aliases."""
    if pre_fn is None:
        pre_fn = return_none
    if post_fn is None:
        post_fn = return_none

    def wrapper_factory(fn: T_Function) -> T_Function:
        """Perform the wrapper factory operation."""
        if inner_fn is None:
            _inner_fn = fn
        else:
            _inner_fn = inner_fn

        @wraps(_inner_fn)
        def wrapped(*args, **kwargs):
            """Perform the wrapped operation."""
            pre_fn(fn, *args, **kwargs)
            result = _inner_fn(*args, **kwargs)
            post_fn(fn, *args, **kwargs)
            return result

        return wrapped  # type: ignore

    return wrapper_factory


class _FunctionRegistry(Generic[T_Output]):
    def __init__(self) -> None:
        """Initialize the instance."""
        fns: Dict[
            Callable[..., T_Output],
            Tuple[Optional[ClassOrTuple], Optional[Predicate], int],
        ] = {}

        super().__init__()
        self.fns = fns

    def register(
        self,
        fn: Callable[[T], T_Output],
        class_or_tuple: Optional[ClassOrTuple] = None,
        *,
        custom_predicate: Optional[Predicate] = None,
        priority: int = 0,
    ) -> Callable[[T], T_Output]:
        """Perform the register operation."""
        return self.register_decorator(
            class_or_tuple,
            custom_predicate=custom_predicate,
            priority=priority,
        )(fn)

    def register_decorator(
        self,
        class_or_tuple: Optional[ClassOrTuple] = None,
        *,
        custom_predicate: Optional[Predicate] = None,
        priority: int = 0,
    ) -> Callable:
        """Perform the register decorator operation."""
        if (class_or_tuple is None) == (custom_predicate is None):
            msg = f"Invalid combinaison of arguments: {class_or_tuple=} and {custom_predicate=}. (only one of them must be None)"
            raise ValueError(msg)

        def _impl(new_fn: Callable[[T], T_Output]) -> Callable[[T], T_Output]:
            """Perform the impl operation."""
            new_value = (class_or_tuple, custom_predicate, priority)
            self.fns = _insert_in_dict(
                self.fns,
                new_fn,
                new_value,
                priority,
                priority_key=2,
            )
            return new_fn

        return _impl

    def apply(
        self,
        x: Any,
        *,
        isinstance_fn: Callable[[Any, Union[type, tuple]], bool] = isinstance,
        unk_mode: UnkMode = "error",
        **kwargs,
    ) -> T_Output:
        """Perform the apply operation."""
        for fn, (class_or_tuple, custom_predicate, _) in self.fns.items():
            if custom_predicate is not None:
                predicate = custom_predicate

            elif class_or_tuple is not None:

                def target_isinstance_fn_wrap(x: Any) -> bool:
                    """Perform the target isinstance fn wrap operation."""
                    return isinstance_fn(x, class_or_tuple)  # type: ignore

                predicate = target_isinstance_fn_wrap
            else:
                msg = f"Invalid function registered. (found {class_or_tuple=} and {custom_predicate=})"
                raise TypeError(msg)

            if predicate(x):
                return fn(x, **kwargs)

        if unk_mode == "identity":
            return x
        elif unk_mode == "error":
            valid_types = [
                class_or_tuple
                for class_or_tuple, _, _ in self.fns.values()
                if class_or_tuple is not None
            ]
            msg = f"Invalid argument type {type(x)}. (expected one of {tuple(valid_types)})"
            raise TypeError(msg)
        else:
            msg = f"Invalid argument {unk_mode=}. (expected one of {get_args(UnkMode)})"
            raise ValueError(msg)


def _insert_in_dict(
    dic: Dict,
    key: Any,
    value: Any,
    priority: int,
    priority_key: int,
) -> Dict:
    """Perform the insert in dict operation."""
    if key in dic:
        return dic
    insert_index = _get_insertion_index(list(dic.values()), priority, priority_key)
    items = list(dic.items())
    items.insert(insert_index, (key, value))
    return dict(items)


def _get_insertion_index(lst: list, priority: int, priority_key: int) -> int:
    """Perform the get insertion index operation."""
    for i, item in enumerate(lst):
        other_priority = item[priority_key]
        if priority >= other_priority:
            return i
    return len(lst)


@overload
def warn_once(
    message: str,
    category: Optional[Type[Warning]] = None,
    stacklevel: int = 1,
    source: Any = None,
) -> None:
    """Warn message once using warnings module."""
    ...


@overload
def warn_once(
    message: Warning,
    category: Any = None,
    stacklevel: int = 1,
    source: Any = None,
) -> None:
    """Warn message once using warnings module."""
    ...


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
        """Perform the inner pre fn operation."""
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
) -> Callable[[T_Function], T_Function]:
    """Perform the deprecated function operation."""
    ...


@overload
def deprecated_function(
    fn: T_Function,
    /,
    *,
    msg_fmt: str = "Deprecated call to '{fn_name}'.",
    warn_fn: Callable[[str], Any] = partial(warn_once, category=DeprecationWarning),
) -> T_Function:
    """Perform the deprecated function operation."""
    ...


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
        """Perform the inner pre fn operation."""
        msg = msg_fmt.format(fn_name=fn.__qualname__)
        warn_fn(msg)
        pre_fn(fn, *args, **kwargs)

    decorator = _decorator_factory(None, pre_fn=inner_pre_fn, post_fn=post_fn)
    if fn is None:
        return decorator
    else:
        return decorator(fn)
