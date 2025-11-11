#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import MISSING, dataclass
from typing import Any, Callable, Dict, Optional, Type, TypeVar, overload

from pythonwrench.typing.checks import is_dataclass_instance  # noqa: F401
from pythonwrench.typing.classes import DataclassInstance

T = TypeVar("T")


def get_defaults_values(obj: DataclassInstance) -> Dict[str, Any]:
    defaults = {}

    for field in obj.__dataclass_fields__.values():
        if callable(field.default_factory):
            default = field.default_factory()
        else:
            default = field.default

        if default != MISSING:
            defaults[field.name] = default

    return defaults


@overload
def dataclassdict(
    cls: Type[T],
    /,
    *,
    init: bool = True,
    repr: bool = True,
    eq: bool = True,
    order: bool = False,
    unsafe_hash: bool = False,
    frozen: bool = False,
) -> Type[T]: ...


@overload
def dataclassdict(
    cls: None = None,
    /,
    *,
    init: bool = True,
    repr: bool = True,
    eq: bool = True,
    order: bool = False,
    unsafe_hash: bool = False,
    frozen: bool = False,
) -> Callable[[Type[T]], Type[T]]: ...


def dataclassdict(
    cls: Optional[Type] = None,
    /,
    *,
    init: bool = True,
    repr: bool = True,
    eq: bool = True,
    order: bool = False,
    unsafe_hash: bool = False,
    frozen: bool = False,
    # match_args: bool=True,
    # kw_only: bool=False,
    # slots: bool=False,
):
    cls_ = dataclass(
        cls,
        init=init,
        repr=repr,
        eq=eq,
        order=order,
        unsafe_hash=unsafe_hash,
        frozen=frozen,
        # match_args=match_args,
        # kw_only=kw_only,
        # slots=slots,
    )

    for attr_name in ("keys", "values", "items", "__len__", "__getitem__"):
        setattr(cls_, attr_name, getattr(cls_.__dict__, attr_name))

    return cls_
