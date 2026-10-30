#!/usr/bin/env python

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
    argv: Optional[Iterable[str]] = None,
    parser: Optional[ArgumentParser] = None,
    list_parsing: ListParsing = "argparse",
    bool_action: BoolAction = "store",
    add_dashed_arg: bool = True,
    return_single_namespace: Literal[True],
    posonly_for_required: bool = False,
    positionals: Iterable[str] = (),
) -> Namespace: ...


@overload
def parse_args_using_dataclass(
    dataclass_type: Type[T_DataclassInstance],
    *,
    argv: Optional[Iterable[str]] = None,
    parser: Optional[ArgumentParser] = None,
    list_parsing: ListParsing = "argparse",
    bool_action: BoolAction = "store",
    add_dashed_arg: bool = True,
    return_single_namespace: Literal[False] = False,
    posonly_for_required: bool = False,
    positionals: Iterable[str] = (),
) -> T_DataclassInstance: ...


@overload
def parse_args_using_dataclass(
    dataclass_type: Type[T_DataclassInstance],
    dataclass_type_2: Type[T_DataclassInstance_2],
    /,
    *,
    argv: Optional[Iterable[str]] = None,
    parser: Optional[ArgumentParser] = None,
    list_parsing: ListParsing = "argparse",
    bool_action: BoolAction = "store",
    add_dashed_arg: bool = True,
    return_single_namespace: Literal[False] = False,
    posonly_for_required: bool = False,
    positionals: Iterable[str] = (),
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
    argv: Optional[Iterable[str]] = None,
    parser: Optional[ArgumentParser] = None,
    list_parsing: ListParsing = "argparse",
    bool_action: BoolAction = "store",
    add_dashed_arg: bool = True,
    return_single_namespace: Literal[False] = False,
    posonly_for_required: bool = False,
    positionals: Iterable[str] = (),
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
    argv: Optional[Iterable[str]] = None,
    parser: Optional[ArgumentParser] = None,
    list_parsing: ListParsing = "argparse",
    bool_action: BoolAction = "store",
    add_dashed_arg: bool = True,
    return_single_namespace: Literal[False] = False,
    posonly_for_required: bool = False,
    positionals: Iterable[str] = (),
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
    argv: Optional[Iterable[str]] = None,
    parser: Optional[ArgumentParser] = None,
    list_parsing: ListParsing = "argparse",
    bool_action: BoolAction = "store",
    add_dashed_arg: bool = True,
    return_single_namespace: Literal[False] = False,
    posonly_for_required: bool = False,
    positionals: Iterable[str] = (),
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
    argv: Optional[Iterable[str]] = None,
    parser: Optional[ArgumentParser] = None,
    list_parsing: ListParsing = "argparse",
    bool_action: BoolAction = "store",
    add_dashed_arg: bool = True,
    return_single_namespace: bool = False,
    posonly_for_required: bool = False,
    positionals: Iterable[str] = (),
) -> Union[
    DataclassInstance,
    Tuple[DataclassInstance, ...],
    Namespace,
]:
    """Converts prog args to a typed dataclass using argparse.

    Currently only supports dataclasses that contains only builtin scalars: str, int, float, None, bool OR list of builtin scalars.

    Args:
        dataclass_type: Target dataclass type to convert to.
        *dataclass_type: Others dataclass types.
        argv: Arguments value given. If None, use sys.argv arguments.
        parser: Optional ArgumentParser to update and parse.
        list_parsing: Defines how Iterables should be handled.
            If "argparse", it uses nargs="*", which follows argparse convention.
            If "brackets", it excepts 1 arguments surrounded by squared brackets e.g. [a,b]
        bool_action: Define how boolean are handled.
            "store": boolean value mlust be explicitely provided with "--arg true" or "--arg false".
        add_dashed_arg: If argument name has underscore, add dashed variant.
            e.g. --arg_number/--arg-number.
        return_single_namespace: If True, avoid parsing argv to dataclass and return argparse.Namespace instance.
        posonly_for_required: If True, make all required arguments positional by default.
        positionals: List of fields considered as positional.
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
            positionals=positionals,
        )
    assert parser is not None

    parsed, other_args = parser.parse_known_args(argv)
    if len(other_args) > 0:
        msg = f"Found {len(other_args)} unknown arguments: {other_args}. (with source {argv=})"
        raise ValueError(msg)

    if return_single_namespace:
        return parsed

    accept_more_args = (init_parser is not None) or (len(dataclass_types) != 1)
    # breakpoint()  # TODO
    dataclass_insts = _instantiate_dataclasses(
        dataclass_types,
        parsed,
        accept_more_args=accept_more_args,
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

    subparser_fields = {
        field.name
        for dcls_type in dcls_types
        for field in fields(dcls_type)
        if _is_dataclass_or_union_of_dataclasses(field.type)
    }
    base_kwds = {
        k: v for k, v in parsed.items() if "." not in k and k not in subparser_fields
    }

    dcls_insts = []

    for dcls_type_i in dcls_types:
        sub_dclasses = {
            field.name: field.type
            for field in fields(dcls_type_i)
            if _is_dataclass_or_union_of_dataclasses(field.type)
        }

        kwds_i = copy.copy(base_kwds)
        for name, dcls_union in sub_dclasses.items():
            selected = parsed.get(name)
            if selected is None:
                # note: an optional subparser that was not selected is None,
                # it must not replace the dataclass field's default/default_factory.
                continue

            if _is_union_type(dcls_union):
                dclasses = get_args(dcls_union)
                dclasses_names = {dcls.__name__: dcls for dcls in dclasses}
                try:
                    dclass_type = dclasses_names[selected]
                except KeyError as err:
                    msg = f"Invalid subparser {selected!r} for field {name!r}."
                    raise ValueError(msg) from err
            else:
                dclass_type = dcls_union

            field_prefix = f"{name}."
            field_kwds = {
                key[len(field_prefix) :]: value
                for key, value in parsed.items()
                if key.startswith(field_prefix)
            }
            dclass_inst = _instantiate_dataclasses(
                (dclass_type,),  # type: ignore
                parsed=field_kwds,
                accept_more_args=True,
            )[0]
            kwds_i[name] = dclass_inst

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
    parser: Optional[ArgumentParser] = None,
    list_parsing: ListParsing = "argparse",
    bool_action: BoolAction = "store",
    add_dashed_arg: bool = True,
    posonly_for_required: bool = False,
    argprefix: str = "",
    positionals: Iterable[str] = (),
) -> ArgumentParser:
    """Perform the add dataclass fields to parser operation."""
    if parser is None:
        parser = ArgumentParser()
    positionals = dict.fromkeys(positionals)

    for field in fields(dataclass_type):
        help = getattr(field, "doc", None)
        if help is None and isinstance(field.metadata.get("doc"), str):
            help = field.metadata["doc"]

        kwds: dict[str, Any] = {
            "help": help,
        }

        if field.default is MISSING and field.default_factory is MISSING:
            if bool_action != "store" and field.type is bool:
                msg = f"Invalid arguments: boolean '{field.name}' without default value is incompatible with {bool_action=}."
                raise RuntimeError(msg)
            required = True

        elif field.default is not MISSING:
            kwds["default"] = field.default
            required = False

        elif field.default_factory is not MISSING:
            kwds["default"] = field.default_factory()
            required = False

        else:
            msg = f"Invalid field '{field.name}': found values for default and default_factory for the same field."
            raise ValueError(msg)

        if is_dataclass_type(field.type):
            subclasses = (field.type,)
        elif _is_union_of_dataclasses(field.type):
            subclasses = get_args(field.type)
        else:
            subclasses = None

        is_positional_only = (required and posonly_for_required) or (
            field.name in positionals
        )

        kw_only = getattr(field, "kw_only", False)
        if is_positional_only and kw_only:
            msg = f"Incompatible arguments for '{field.name}': found {required=}, {posonly_for_required=} but {kw_only=}."
            raise ValueError(msg)

        if not is_positional_only:
            # note: required option is invalid for posonly arg
            kwds["required"] = required

        if subclasses is None:
            if is_positional_only:
                prefix = argprefix
            else:
                prefix = f"--{argprefix}"

            posargs = [f"{prefix}{field.name}"]
            if add_dashed_arg and "_" in field.name:
                dashed_arg_name = field.name.replace("_", "-")
                posargs.append(f"{prefix}{dashed_arg_name}")

            try:
                inner_kwds = _get_kwds_for_type(field.type, list_parsing, bool_action)
                kwds.update(inner_kwds)
            except (ValueError, TypeError, RuntimeError) as err:
                msg = f"Invalid field '{field.name}': field type '{field.type}' is not supported."
                raise type(err)(msg) from err

            if is_positional_only and "nargs" not in kwds and not required:
                kwds["nargs"] = "?"

            parser.add_argument(*posargs, **kwds)

        else:
            subparsers = parser.add_subparsers(
                dest=f"{argprefix}{field.name}",
                required=kwds.get("required", False),
                help=kwds.get("help", None),
            )
            for subcls in subclasses:
                subparser = subparsers.add_parser(subcls.__name__)
                add_dataclass_fields_to_parser(
                    subcls,
                    parser=subparser,
                    list_parsing=list_parsing,
                    bool_action=bool_action,
                    add_dashed_arg=add_dashed_arg,
                    posonly_for_required=posonly_for_required,
                    argprefix=f"{argprefix}{field.name}.",
                    positionals=positionals,
                )

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


def _is_dataclass_or_union_of_dataclasses(x: Any) -> bool:
    return is_dataclass_type(x) or _is_union_of_dataclasses(x)


def _is_union_of_dataclasses(x: Any) -> bool:
    return _is_union_type(x) and all(
        is_dataclass_type(subcls) for subcls in get_args(x)
    )


# ALIASES
@deprecated_alias(add_dataclass_fields_to_parser)
def new_parser_from_dataclass(*args, **kwargs):
    """Perform the new parser from dataclass operation."""
