#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
from argparse import ArgumentParser, Namespace
from dataclasses import MISSING, fields
from typing import (
    Any,
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
    overload,
)

from pythonwrench.argparse.parsers import (
    ListParsing,
    _is_iterable_type_like,
    _is_literal_type,
    _is_union_type,
    _search_parse_fn,
)
from pythonwrench.collections import unflat_dict_of_dict
from pythonwrench.functools import filter_and_call
from pythonwrench.typing.checks import is_dataclass_type
from pythonwrench.typing.classes import (
    Dataclass,
    DataclassInstance,
)
from pythonwrench.warnings import deprecated_alias

try:
    from argparse import BooleanOptionalAction  # type: ignore
except ImportError:

    class BooleanOptionalAction: ...


T_Dataclass = TypeVar("T_Dataclass", bound=Dataclass)
T_DataclassInstance = TypeVar("T_DataclassInstance", bound=DataclassInstance)
T_DataclassInstance_2 = TypeVar("T_DataclassInstance_2", bound=DataclassInstance)
T_DataclassInstance_3 = TypeVar("T_DataclassInstance_3", bound=DataclassInstance)
T_DataclassInstance_4 = TypeVar("T_DataclassInstance_4", bound=DataclassInstance)
T_DataclassInstance_5 = TypeVar("T_DataclassInstance_5", bound=DataclassInstance)

_BoolActionName = Literal["store", "store_true", "store_false", "bool_optional"]
BoolAction = Union[_BoolActionName, Type[BooleanOptionalAction]]


@overload
def parse_args_using_dataclass(
    dataclass_type: Type[DataclassInstance],
    *dataclass_types: Type[DataclassInstance],
    args: Optional[Iterable[str]] = None,
    parser: Optional[ArgumentParser] = None,
    list_parsing: ListParsing = "argparse",
    bool_action: BoolAction = "store",
    add_dashed_arg: bool = True,
    return_single_namespace: Literal[True],
    posonly_for_required: bool = False,
) -> Namespace: ...


@overload
def parse_args_using_dataclass(
    dataclass_type: Type[T_DataclassInstance],
    *,
    args: Optional[Iterable[str]] = None,
    parser: Optional[ArgumentParser] = None,
    list_parsing: ListParsing = "argparse",
    bool_action: BoolAction = "store",
    add_dashed_arg: bool = True,
    return_single_namespace: Literal[False] = False,
    posonly_for_required: bool = False,
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
    bool_action: BoolAction = "store",
    add_dashed_arg: bool = True,
    return_single_namespace: Literal[False] = False,
    posonly_for_required: bool = False,
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
    bool_action: BoolAction = "store",
    add_dashed_arg: bool = True,
    return_single_namespace: Literal[False] = False,
    posonly_for_required: bool = False,
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
    bool_action: BoolAction = "store",
    add_dashed_arg: bool = True,
    return_single_namespace: Literal[False] = False,
    posonly_for_required: bool = False,
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
    bool_action: BoolAction = "store",
    add_dashed_arg: bool = True,
    return_single_namespace: Literal[False] = False,
    posonly_for_required: bool = False,
) -> Tuple[
    T_DataclassInstance,
    T_DataclassInstance_2,
    T_DataclassInstance_3,
    T_DataclassInstance_4,
    T_DataclassInstance_5,
]: ...


def parse_args_using_dataclass(
    dataclass_type: Dataclass,
    *dataclass_types: Dataclass,
    args: Optional[Iterable[str]] = None,
    parser: Optional[ArgumentParser] = None,
    list_parsing: ListParsing = "argparse",
    bool_action: BoolAction = "store",
    add_dashed_arg: bool = True,
    return_single_namespace: bool = False,
    posonly_for_required: bool = False,
) -> Union[
    DataclassInstance,
    Tuple[DataclassInstance, ...],
    Namespace,
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
            bool_action=bool_action,
            add_dashed_arg=add_dashed_arg,
            posonly_for_required=posonly_for_required,
        )
    assert parser is not None

    parsed, argv = parser.parse_known_args(args)
    if len(argv) > 0:
        msg = f"Found {len(argv)} unknown arguments: {argv}."
        raise ValueError(msg)

    if return_single_namespace:
        return parsed

    accept_more_args = (init_parser is not None) or (len(dataclass_types) != 1)
    # breakpoint()  # TODO
    dataclass_insts = _instantiate_dataclasses(
        dataclass_types, parsed, accept_more_args=accept_more_args
    )

    if len(dataclass_insts) == 1:
        return dataclass_insts[0]
    else:
        return tuple(dataclass_insts)


def _instantiate_dataclasses(
    dcls_types: Tuple[Dataclass, ...],
    parsed: Union[Namespace, Dict[str, Any]],
    accept_more_args: bool,
) -> List[DataclassInstance]:
    if isinstance(parsed, Namespace):
        parsed = parsed.__dict__
    sub_kwds = {k: v for k, v in parsed.items() if "." in k}
    unflat_sub_kwds = unflat_dict_of_dict(sub_kwds, overwrite=False)
    choices_kwds = {k: v for k, v in parsed.items() if k in unflat_sub_kwds}
    base_kwds = {
        k: v for k, v in parsed.items() if k not in sub_kwds and k not in choices_kwds
    }
    assert set(unflat_sub_kwds) == set(choices_kwds)

    dcls_insts = []

    for dcls_type_i in dcls_types:
        sub_dclasses = {
            field.name: field.type
            for field in fields(dcls_type_i)
            if is_dataclass_type(field.type) or _is_union_of_dataclasses(field.type)
        }

        kwds_i = copy.copy(base_kwds)
        for name, dcls_union in sub_dclasses.items():
            if _is_union_type(dcls_union):
                dclasses = get_args(dcls_union)
                dclasses_names = {dcls.__name__: dcls for dcls in dclasses}
                dclass_type = dclasses_names[choices_kwds[name]]
            else:
                dclass_type = dcls_union

            try:
                dclass = _instantiate_dataclasses(
                    (dclass_type,),  # type: ignore
                    parsed=unflat_sub_kwds[name],
                    accept_more_args=True,
                )[0]
            except KeyError:
                # breakpoint()  # TODO
                raise
            kwds_i[name] = dclass

        if accept_more_args:
            instance = filter_and_call(
                dcls_type_i,
                _fill_all_arguments=True,
                **kwds_i,
            )
        else:
            instance = dcls_type_i(**kwds_i)

        dcls_insts.append(instance)

    return dcls_insts


def add_dataclass_fields_to_parser(
    dataclass_type: Type[T_DataclassInstance],
    *,
    parser: Optional[ArgumentParser],
    list_parsing: ListParsing = "argparse",
    bool_action: BoolAction = "store",
    add_dashed_arg: bool = True,
    posonly_for_required: bool = False,
    argprefix: str = "",
) -> ArgumentParser:
    """Perform the add dataclass fields to parser operation."""
    if posonly_for_required:
        prefix = argprefix
    else:
        prefix = f"--{argprefix}"

    if parser is None:
        parser = ArgumentParser()

    for field in fields(dataclass_type):
        kwds = {}
        posargs = [f"{prefix}{field.name}"]
        if add_dashed_arg and "_" in field.name:
            dashed_arg_name = field.name.replace("_", "-")
            posargs.append(f"{prefix}{dashed_arg_name}")

        if field.default is MISSING and field.default_factory is MISSING:
            if bool_action != "store" and field.type is bool:
                msg = f"Invalid arguments: boolean '{field.name}' without default value is incompatible with {bool_action=}."
                raise RuntimeError(msg)
            kwds["required"] = True

        elif field.default is not MISSING:
            kwds["default"] = field.default
        elif field.default_factory is not MISSING:
            kwds["default"] = field.default_factory()  # type: ignore
        else:
            msg = f"Invalid field '{field.name}': found values for default and default_factory."
            raise ValueError(msg)

        if is_dataclass_type(field.type):
            subclasses = (field.type,)
        elif _is_union_of_dataclasses(field.type):
            subclasses = get_args(field.type)
        else:
            subclasses = None

        if subclasses is not None:
            subparsers = parser.add_subparsers(
                dest=field.name,
                required=kwds.get("required", False),
            )
            for subcls in subclasses:
                subparser = subparsers.add_parser(subcls.__name__)
                _ = add_dataclass_fields_to_parser(
                    subcls,
                    parser=subparser,
                    list_parsing=list_parsing,
                    bool_action=bool_action,
                    add_dashed_arg=add_dashed_arg,
                    posonly_for_required=posonly_for_required,
                    argprefix=f"{argprefix}{field.name}.",
                )

        else:
            try:
                inner_kwds = _get_kwds_for_type(field.type, list_parsing, bool_action)
            except (ValueError, TypeError, RuntimeError) as err:
                msg = f"Invalid field '{field.name}': field type '{field.type}' is not supported."
                raise type(err)(msg) from err

            kwds.update(inner_kwds)

            posargs = [arg.split(".")[-1] for arg in posargs]
            parser.add_argument(*posargs, **kwds)

    # TODO
    # breakpoint()
    return parser


def _get_kwds_for_type(
    field_type: Any,
    list_parsing: Optional[ListParsing],
    bool_action: BoolAction,
) -> Dict[str, Any]:
    """Perform the get kwds for type operation."""
    if bool_action == "bool_optional":
        bool_action = BooleanOptionalAction
    kwds = {}

    if bool_action != "store" and field_type is bool:
        kwds["action"] = bool_action
        return kwds

    elif list_parsing == "argparse" and _is_iterable_type_like(field_type):
        type_args = get_args(field_type)
        if isinstance(type_args, tuple) and len(type_args) == 1:
            item_type = type_args[0]
            kwds = _get_kwds_for_type(
                item_type, list_parsing=None, bool_action=bool_action
            )
        kwds["nargs"] = "*"
        return kwds

    parse_fn = _search_parse_fn(field_type, list_parsing=list_parsing)

    if parse_fn is not None:
        kwds["type"] = parse_fn
        if _is_literal_type(field_type):
            kwds["choices"] = get_args(field_type)
        return kwds

    else:
        msg = (
            f"Unsupported type {field_type}. (with {list_parsing=} and {bool_action=})"
        )
        raise TypeError(msg)


def _is_union_of_dataclasses(x: Any) -> bool:
    return _is_union_type(x) and all(
        is_dataclass_type(subcls) for subcls in get_args(x)
    )


# ALIASES
@deprecated_alias(add_dataclass_fields_to_parser)
def new_parser_from_dataclass(*args, **kwargs):
    """Perform the new parser from dataclass operation."""
    ...
