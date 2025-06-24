#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Literal,
    Optional,
    Tuple,
    TypeVar,
    Union,
    get_args,
)

from typing_extensions import ParamSpec

P = ParamSpec("P")
T = TypeVar("T")
U = TypeVar("U")
T_Output = TypeVar("T_Output")

UnkMode = Literal["identity", "error"]
ClassOrTuple = Union[type, Tuple[type, ...]]
Predicate = Callable[[Any], bool]


def return_none(*args, **kwargs) -> None:
    """Return None function placeholder."""
    return None


def _decorator_factory(
    inner_fn: Optional[Callable[P, U]],
    *,
    pre_fn: Callable[..., Any] = return_none,
    post_fn: Callable[..., Any] = return_none,
) -> Callable[..., Callable[P, U]]:
    """Deprecated decorator for function aliases."""

    def wrapper_factory(fn: Callable[P, U]) -> Callable[P, U]:
        if inner_fn is None:
            _inner_fn = fn
        else:
            _inner_fn = inner_fn

        @wraps(_inner_fn)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> U:
            pre_fn(fn, *args, **kwargs)
            result = _inner_fn(*args, **kwargs)
            post_fn(fn, *args, **kwargs)
            return result

        return wrapped

    return wrapper_factory


class _FunctionRegistry(Generic[T_Output]):
    def __init__(self) -> None:
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
        return self.register_decorator(
            class_or_tuple, custom_predicate=custom_predicate
        )(fn)

    def register_decorator(
        self,
        class_or_tuple: Optional[ClassOrTuple] = None,
        *,
        custom_predicate: Optional[Predicate] = None,
        priority: int = 0,
    ) -> Callable:
        if (class_or_tuple is None) == (custom_predicate is None):
            msg = f"Invalid combinaison of arguments: {class_or_tuple=} and {custom_predicate=}. (only one of them must be None)"
            raise ValueError(msg)

        def _impl(new_fn: Callable[[T], T_Output]) -> Callable[[T], T_Output]:
            new_fns = {}
            inserted = False

            for fn_i, (
                class_or_tuple_i,
                custom_predicate_i,
                priority_i,
            ) in self.fns.items():
                if new_fn == fn_i:
                    continue

                if not inserted and priority >= priority_i:
                    new_fns[new_fn] = (class_or_tuple, custom_predicate, priority)
                    inserted = True

                new_fns[fn_i] = (class_or_tuple_i, custom_predicate_i, priority_i)

            if not inserted:
                assert all(
                    priority < priority_i for _, _, priority_i in self.fns.values()
                )
                new_fns[new_fn] = (class_or_tuple, custom_predicate, priority)

            assert new_fn in new_fns
            self.fns = new_fns
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
        for fn, (class_or_tuple, custom_predicate, _) in self.fns.items():
            if custom_predicate is not None:
                predicate = custom_predicate

            elif class_or_tuple is not None:

                def target_isinstance_fn_wrap(x: Any) -> bool:
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
