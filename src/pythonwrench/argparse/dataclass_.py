#!/usr/bin/env python
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from dataclasses import MISSING, fields
from typing import (
    Any,
    Dict,
    Iterable,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
    overload,
)

from pythonwrench.argparse.parsers import (
    ListParsing,
    _search_parse_fn,
    get_parse_fn,
)
from pythonwrench.functools import filter_and_call
from pythonwrench.typing.checks import (
    _is_iterable_type_like,
    _is_literal_type,
    _is_optional_type,
    _is_union_type,
)
from pythonwrench.typing.classes import (
    Dataclass,
    DataclassInstance,
    NoneType,
)
from pythonwrench.warnings import deprecated_alias

T_Dataclass = TypeVar("T_Dataclass", bound=Dataclass)
T_DataclassInstance = TypeVar("T_DataclassInstance", bound=DataclassInstance)
T_DataclassInstance_2 = TypeVar("T_DataclassInstance_2", bound=DataclassInstance)
T_DataclassInstance_3 = TypeVar("T_DataclassInstance_3", bound=DataclassInstance)
T_DataclassInstance_4 = TypeVar("T_DataclassInstance_4", bound=DataclassInstance)
T_DataclassInstance_5 = TypeVar("T_DataclassInstance_5", bound=DataclassInstance)

_SCALARS_TARGET_TYPES = (str, int, float, None, NoneType, bool)


@overload
def parse_args_using_dataclass(
    dataclass_type: Type[T_DataclassInstance],
    *,
    args: Optional[Iterable[str]] = None,
    parser: Optional[ArgumentParser] = None,
    list_parsing: ListParsing = "argparse",
    add_dashed_arg: bool = True,
) -> T_DataclassInstance: ...


@overload
def parse_args_using_dataclass(
    dataclass_type: Type[T_DataclassInstance],
    dataclass_type_2: Type[T_DataclassInstance_2],
    /,
    *,
    args: Optional[Iterable[str]] = None,
    parser: Optional[ArgumentParser] = None,
    list_parsing: ListParsing = "argparse",
    add_dashed_arg: bool = True,
) -> Tuple[
    T_DataclassInstance,
    T_DataclassInstance_2,
]: ...


@overload
def parse_args_using_dataclass(
    dataclass_type: Type[T_DataclassInstance],
    dataclass_type_2: Type[T_DataclassInstance_2],
    dataclass_type_3: Type[T_DataclassInstance_3],
    /,
    *,
    args: Optional[Iterable[str]] = None,
    parser: Optional[ArgumentParser] = None,
    list_parsing: ListParsing = "argparse",
    add_dashed_arg: bool = True,
) -> Tuple[
    T_DataclassInstance,
    T_DataclassInstance_2,
    T_DataclassInstance_3,
]: ...


@overload
def parse_args_using_dataclass(
    dataclass_type: Type[T_DataclassInstance],
    dataclass_type_2: Type[T_DataclassInstance_2],
    dataclass_type_3: Type[T_DataclassInstance_3],
    dataclass_type_4: Type[T_DataclassInstance_4],
    /,
    *,
    args: Optional[Iterable[str]] = None,
    parser: Optional[ArgumentParser] = None,
    list_parsing: ListParsing = "argparse",
    add_dashed_arg: bool = True,
) -> Tuple[
    T_DataclassInstance,
    T_DataclassInstance_2,
    T_DataclassInstance_3,
    T_DataclassInstance_4,
]: ...


@overload
def parse_args_using_dataclass(
    dataclass_type: Type[T_DataclassInstance],
    dataclass_type_2: Type[T_DataclassInstance_2],
    dataclass_type_3: Type[T_DataclassInstance_3],
    dataclass_type_4: Type[T_DataclassInstance_4],
    dataclass_type_5: Type[T_DataclassInstance_5],
    /,
    *,
    args: Optional[Iterable[str]] = None,
    parser: Optional[ArgumentParser] = None,
    list_parsing: ListParsing = "argparse",
    add_dashed_arg: bool = True,
) -> Tuple[
    T_DataclassInstance,
    T_DataclassInstance_2,
    T_DataclassInstance_3,
    T_DataclassInstance_4,
    T_DataclassInstance_5,
]: ...


def parse_args_using_dataclass(
    dataclass_type: Type[DataclassInstance],
    *dataclass_types: Type[DataclassInstance],
    args: Optional[Iterable[str]] = None,
    parser: Optional[ArgumentParser] = None,
    list_parsing: ListParsing = "argparse",
    add_dashed_arg: bool = True,
) -> Union[
    DataclassInstance,
    Tuple[DataclassInstance, ...],
]:
    """Converts prog args to a typed dataclass using argparse.

    Currently only supports dataclasses that contains only builtin scalars: str, int, float, None, bool OR list of builtin scalars.
    """
    init_parser = parser
    dataclass_types = (dataclass_type,) + dataclass_types
    del dataclass_type

    for dataclass_type_i in dataclass_types:
        parser = add_dataclass_fields_to_parser(
            dataclass_type_i,
            parser=parser,
            list_parsing=list_parsing,
            add_dashed_arg=add_dashed_arg,
        )
    assert parser is not None

    parsed, argv = parser.parse_known_args(args)
    if len(argv) > 0:
        msg = f"Found {len(argv)} unknown arguments: {argv}."
        raise ValueError(msg)

    dataclass_insts = []
    for dataclass_type_i in dataclass_types:
        if init_parser is None and len(dataclass_types) == 1:
            instance = dataclass_type_i(**parsed.__dict__)
        else:
            instance = filter_and_call(
                dataclass_type_i,
                _fill_all_arguments=True,
                **parsed.__dict__,
            )
        dataclass_insts.append(instance)

    if len(dataclass_insts) == 1:
        return dataclass_insts[0]
    else:
        return tuple(dataclass_insts)


def add_dataclass_fields_to_parser(
    dataclass_type: Type[T_DataclassInstance],
    *,
    parser: Optional[ArgumentParser],
    list_parsing: ListParsing = "argparse",
    add_dashed_arg: bool = True,
) -> ArgumentParser:
    """Perform the add dataclass fields to parser operation."""
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


def _get_kwds_for_type(
    field_type: Any,
    list_parsing: Optional[ListParsing] = "argparse",
) -> Dict[str, Any]:
    """Perform the get kwds for type operation."""
    kwds = {}
    type_args = get_args(field_type)

    parse_fn = _search_parse_fn(field_type, list_parsing=list_parsing)
    if parse_fn is not None:
        kwds["type"] = parse_fn
        if _is_literal_type(field_type):
            kwds["choices"] = type_args

    elif _is_iterable_type_like(field_type) and list_parsing == "argparse":
        if isinstance(type_args, tuple) and len(type_args) == 1:
            item_type = type_args[0]
            kwds = _get_kwds_for_type(item_type, list_parsing=None)
        kwds["nargs"] = "*"

    else:
        msg = f"Unsupported type {field_type}. (with {list_parsing=})"
        raise TypeError(msg)

    return kwds


def _get_kwds_for_scalar_type(
    type_: Any,
    from_field_type: Any,
    list_parsing: ListParsing,
) -> Dict[str, Any]:
    """Perform the get kwds for scalar type operation."""
    kwds = {}

    if (
        type_ in _SCALARS_TARGET_TYPES
        or _is_optional_type(type_)
        or _is_union_type(type_)
        or (
            _is_iterable_type_like(get_origin(from_field_type))
            and list_parsing == "brackets"
        )
    ):
        pass

    elif _is_literal_type(type_):
        type_args = get_args(type_)
        kwds["choices"] = type_args
    else:
        msg = f"Unsupported dataclass member type {type_} from {from_field_type}."
        raise TypeError(msg)

    kwds["type"] = get_parse_fn(type_, list_parsing=list_parsing)  # type: ignore
    return kwds


# ALIASES
@deprecated_alias(add_dataclass_fields_to_parser)
def new_parser_from_dataclass(*args, **kwargs):
    """Perform the new parser from dataclass operation."""
    ...
