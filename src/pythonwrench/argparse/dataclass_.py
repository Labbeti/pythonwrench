#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from argparse import ArgumentParser
from collections.abc import Iterable as _Iterable
from dataclasses import MISSING, fields
from functools import partial
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

try:
    from types import UnionType
except ImportError:
    # support older python versions
    UnionType = Any

from pythonwrench._core import _FunctionRegistry, _insert_in_dict
from pythonwrench.functools import filter_and_call, function_alias
from pythonwrench.typing.classes import Dataclass, DataclassInstance, NoneType
from pythonwrench.warnings import deprecated_alias
from pythonwrench.argparse.parsers import (
    ListParsing,
    get_parse_fn,
    _is_iterable_type_like,
)

T_Dataclass = TypeVar("T_Dataclass", bound=Dataclass)
T_DataclassInstance = TypeVar("T_DataclassInstance", bound=DataclassInstance)

_SCALARS_TARGET_TYPES = (str, int, float, None, NoneType, bool)


def parse_args_using_dataclass(
    dataclass_type: Type[T_DataclassInstance],
    *,
    args: Optional[Iterable[str]] = None,
    parser: Optional[ArgumentParser] = None,
    list_parsing: ListParsing = "argparse",
    add_dashed_arg: bool = True,
) -> T_DataclassInstance:
    """Converts prog args to a typed dataclass using argparse.

    Currently only supports dataclasses that contains only builtin scalars: str, int, float, None, bool OR list of builtin scalars.
    """
    init_parser = parser
    parser = add_dataclass_fields_to_parser(
        dataclass_type,
        parser=parser,
        list_parsing=list_parsing,
        add_dashed_arg=add_dashed_arg,
    )
    parsed, argv = parser.parse_known_args(args)
    if len(argv) > 0:
        raise ValueError(f"Found {len(argv)} unknown arguments: {argv}.")

    if init_parser is None:
        instance = dataclass_type(**parsed.__dict__)
    else:
        instance = filter_and_call(
            dataclass_type,
            _fill_all_arguments=True,
            **parsed.__dict__,
        )
    return instance


def add_dataclass_fields_to_parser(
    dataclass_type: Type[T_DataclassInstance],
    *,
    parser: Optional[ArgumentParser],
    list_parsing: ListParsing = "argparse",
    add_dashed_arg: bool = True,
) -> ArgumentParser:
    if parser is None:
        parser = ArgumentParser()

    for field in fields(dataclass_type):
        kwds = {}
        posargs = [f"--{field.name}"]
        if add_dashed_arg and "_" in field.name:
            dashed_arg_name = field.name.replace("_", "-")
            posargs.append(f"--{dashed_arg_name}")

        if field.default is MISSING and field.default_factory is MISSING:
            kwds["required"] = True
        elif field.default is not MISSING:
            kwds["default"] = field.default
        elif field.default_factory is not MISSING:
            kwds["default"] = field.default_factory()  # type: ignore

        else:
            msg = f"Invalid field {field.name}: found values for default and default_factory."
            raise ValueError(msg)

        try:
            inner_kwds = _get_kwds_for_type(field.type, list_parsing)
        except (ValueError, TypeError, RuntimeError) as err:
            msg = f"Invalid field {field.name}: field type '{field.type}' is not supported."
            raise type(err)(msg) from err

        kwds.update(inner_kwds)
        parser.add_argument(*posargs, **kwds)

    return parser


@deprecated_alias(add_dataclass_fields_to_parser)
def new_parser_from_dataclass(*args, **kwargs): ...


def _get_kwds_for_type(
    field_type: Any,
    list_parsing: ListParsing = "argparse",
) -> Dict[str, Any]:
    kwds = {}

    type_origin = get_origin(field_type)
    type_args = get_args(field_type)

    # sanity checks
    if type_origin is Literal:
        if not all(type(arg) in _SCALARS_TARGET_TYPES for arg in type_args):
            msg = f"Invalid argument {field_type=}. (expected homogeneous types in {type_origin})"
            raise TypeError(msg)

    if (
        (field_type in _SCALARS_TARGET_TYPES)
        or (
            type_origin
            in (
                Literal,
                Optional,
                UnionType,
                Union,
            )
        )
        or (_is_iterable_type_like(type_origin) and list_parsing == "brackets")
    ):
        inner_kwds = _get_kwds_for_scalar_type(field_type, field_type, list_parsing)
        kwds.update(inner_kwds)

    elif _is_iterable_type_like(type_origin):
        item_type = type_args[0]
        inner_kwds = _get_kwds_for_scalar_type(item_type, field_type, list_parsing)
        inner_kwds["nargs"] = "*"
        kwds.update(inner_kwds)
    else:
        msg = f"Unsupported type {field_type}. (with {type_origin=})"
        raise TypeError(msg)

    return kwds


def _get_kwds_for_scalar_type(
    type_: Any,
    from_field_type: Any,
    list_parsing: ListParsing,
) -> Dict[str, Any]:
    type_origin = get_origin(type_)
    kwds = {}

    if (
        type_ in _SCALARS_TARGET_TYPES
        or type_origin in (UnionType, Union, Optional)
        or (
            _is_iterable_type_like(get_origin(from_field_type))
            and list_parsing == "brackets"
        )
    ):
        pass

    elif type_origin is Literal:
        type_args = get_args(type_)
        kwds["choices"] = type_args
    else:
        msg = f"Unsupported dataclass member type {type_} from {from_field_type}."
        raise TypeError(msg)

    kwds["type"] = parse_to(type_, list_parsing=list_parsing)  # type: ignore
    return kwds
