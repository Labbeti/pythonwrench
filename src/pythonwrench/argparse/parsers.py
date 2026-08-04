#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from enum import Enum
from functools import partial
from pathlib import Path
from typing import (
    Any,
    Callable,
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

from pythonwrench._core import Predicate
from pythonwrench.argparse._core import (
    _is_iterable_type_like,
    _is_literal,
    _is_optional,
    _is_union,
)
from pythonwrench.typing.classes import NoneType, UnionType
from pythonwrench.warnings import deprecated_alias

T = TypeVar("T")
T_Enum = TypeVar("T_Enum", bound=Enum)
T_Callable = TypeVar("T_Callable", bound=Callable)
TargetType = Union[
    Type[T],
    UnionType,
    "Type[Literal]",
    "Type[Optional]",
    Tuple[type, ...],
]

ListParsing = Literal["argparse", "brackets"]
HandleException = Literal["return", "raise", "ignore"]

DEFAULT_TRUE_VALUES = ("True", "t", "yes", "y", "1")
DEFAULT_FALSE_VALUES = ("False", "f", "no", "n", "0")
DEFAULT_NONE_VALUES = ("None", "null")

_PARSER_REGISTRY: List[Tuple[Union[TargetType, Predicate], Callable]] = []


class ParseError(ValueError): ...


@overload
def register_parser_fn(
    type_: Union[TargetType, Predicate, None],
    fn: None = None,
) -> Callable[[T_Callable], T_Callable]: ...


@overload
def register_parser_fn(
    type_: Union[TargetType, Predicate, None],
    fn: T_Callable,
) -> T_Callable: ...


def register_parser_fn(
    type_: Union[TargetType, Predicate, None],
    fn: Optional[Callable] = None,
) -> Callable:
    global _PARSER_REGISTRY
    if type_ is None:
        type_ = NoneType

    if fn is None:
        return partial(register_parser_fn, type_)
    else:
        for type_or_pred, _ in _PARSER_REGISTRY:
            if type_or_pred is type_:
                return fn
        _PARSER_REGISTRY.append((type_, fn))  # type: ignore
        return fn


def parse_to_type(
    x: str,
    target_type: TargetType[T],
    *,
    case_sensitive: bool = False,
    true_values: Union[str, Iterable[str]] = DEFAULT_TRUE_VALUES,
    false_values: Union[str, Iterable[str]] = DEFAULT_FALSE_VALUES,
    none_values: Union[str, Iterable[str]] = DEFAULT_NONE_VALUES,
    list_parsing: ListParsing = "argparse",
    handle_exception: HandleException = "raise",
) -> T:
    """Convert string values to target type safely. Intended for argparse arguments.

    - True values: 'True', 'T', 'yes', 'y', '1'.
    - False values: 'False', 'F', 'no', 'n', '0'.
    - None values: 'None', 'null'
    - Other raises ParseError.
    """
    parse_fn = get_parse_fn(
        target_type,
        case_sensitive=case_sensitive,
        true_values=true_values,
        false_values=false_values,
        none_values=none_values,
        list_parsing=list_parsing,
        handle_exception=handle_exception,
    )
    output = parse_fn(x)
    return output


def get_parse_fn(
    type_: TargetType[T],
    *,
    case_sensitive: bool = False,
    true_values: Union[str, Iterable[str]] = DEFAULT_TRUE_VALUES,
    false_values: Union[str, Iterable[str]] = DEFAULT_FALSE_VALUES,
    none_values: Union[str, Iterable[str]] = DEFAULT_NONE_VALUES,
    list_parsing: ListParsing = "argparse",
    handle_exception: HandleException = "raise",
) -> Callable[[str], T]:
    """Returns a callable that convert string value to target type safely.

    Intended for argparse arguments.
    """
    kwds = dict(
        case_sensitive=case_sensitive,
        true_values=true_values,
        false_values=false_values,
        none_values=none_values,
        list_parsing=list_parsing,
        handle_exception=handle_exception,
    )
    if type_ is None:
        type_ = NoneType

    parse_fn = None
    for type_or_pred_i, parse_fn_i in _PARSER_REGISTRY:
        if isinstance(type_or_pred_i, type):
            if type_ == type_or_pred_i:
                parse_fn = parse_fn_i
                break
        elif isinstance(type_or_pred_i, Predicate):
            if type_or_pred_i(type_, **kwds) is True:
                parse_fn = partial(parse_fn_i, type_)
                break
        else:
            msg = f"Invalid argument {type_or_pred_i=}. (excepted type or predicate function)"
            raise ValueError(msg)

    if parse_fn is None:
        msg = f"Invalid argument {type_=}. (no valid type or typing found in registry)"
        raise ValueError(msg)

    parse_fn = partial(parse_fn, **kwds)
    return parse_fn


@register_parser_fn(bool)
def parse_to_bool(
    x: str,
    *,
    case_sensitive: bool = False,
    true_values: Union[str, Iterable[str]] = DEFAULT_TRUE_VALUES,
    false_values: Union[str, Iterable[str]] = DEFAULT_FALSE_VALUES,
    handle_exception: HandleException = "raise",
    **kwds,
) -> bool:
    true_values = _sanitize_values(true_values)
    if _str_in(x, true_values, case_sensitive):
        return True

    false_values = _sanitize_values(false_values)
    if _str_in(x, false_values, case_sensitive):
        return False

    values = tuple(true_values + false_values)
    output = ParseError(f"Invalid argument '{x}'. (expected one of {values})")
    return _handle_output(x, handle_exception, output)


@register_parser_fn(float)
def parse_to_float(
    x: str, handle_exception: HandleException = "raise", **kwds
) -> float:
    try:
        return float(x)
    except ValueError as err:
        return _handle_output(x, handle_exception, err)


@register_parser_fn(int)
def parse_to_int(x: str, handle_exception: HandleException = "raise", **kwds) -> int:
    try:
        return int(x)
    except ValueError as err:
        return _handle_output(x, handle_exception, err)


@register_parser_fn(NoneType)
def parse_to_none(
    x: str,
    *,
    case_sensitive: bool = False,
    none_values: Union[str, Iterable[str]] = DEFAULT_NONE_VALUES,
    handle_exception: HandleException = "raise",
    **kwds,
) -> Union[None, Exception]:
    """Convert string values to None safely. Intended for argparse arguments.

    - None values: 'None', 'null'
    - Other raises ValueError.
    """
    none_values = _sanitize_values(none_values)
    if _str_in(x, none_values, case_sensitive):
        return None

    values = tuple(none_values)
    output = ValueError(f"Invalid argument '{x}'. (expected one of {values})")
    return _handle_output(x, handle_exception, output)


@register_parser_fn(Path)
def _parse_to_path(x: str, handle_exception: HandleException = "raise", **kwds) -> Path:
    try:
        return Path(x)
    except (ValueError, TypeError) as err:
        return _handle_output(x, handle_exception, err)


@register_parser_fn(str)
def _parse_to_str(x: str, **kwds) -> str:
    return x


def _is_enum_for_parsing(x: Any, **kwds) -> bool:
    return isinstance(x, type) and issubclass(x, Enum)


def _is_iterable_type_like_for_parsing(
    x: Any,
    *,
    list_parsing: ListParsing = "argparse",
    **kwds,
) -> bool:
    return (list_parsing == "brackets") and _is_iterable_type_like(x)


def _is_literal_for_parsing(x: Any, **kwds) -> bool:
    return _is_literal(x)


def _is_optional_for_parsing(x: Any, **kwds) -> bool:
    return _is_optional(x)


def _is_union_for_parsing(x: Any, **kwds) -> bool:
    return _is_union(x)


@register_parser_fn(_is_enum_for_parsing)
def _parse_to_enum(
    target_type: Type[T_Enum],
    x: str,
    *,
    case_sensitive: bool = False,
    handle_exception: HandleException = "raise",
    **kwds,
) -> T_Enum:
    for enum_value in target_type:
        candidates = [enum_value.name, str(enum_value.value)]
        if _str_in(x, candidates, case_sensitive):
            return enum_value

    msg = f"Invalid argument {x=}. (excepted one of {tuple(target_type)})"
    output = ValueError(msg)
    return _handle_output(x, handle_exception, output)


@register_parser_fn(_is_iterable_type_like_for_parsing)
def _parse_to_list(
    target_type: TargetType[T],
    x: str,
    *,
    list_parsing: ListParsing = "argparse",
    handle_exception: HandleException = "raise",
    **kwds,
) -> T:
    if list_parsing != "brackets":
        msg = f"Cannot convert {x=} to list with {list_parsing=}. (excepted list_parsing='brackets')"
        raise ValueError(msg)

    args = get_args(target_type)

    if len(args) == 0:
        target_item_type = str
    elif len(args) == 1:
        target_item_type = args[0]
    else:
        raise ValueError

    pattern = r"^\s*\[\s*(|.*[^,\s])(|\s*,)\s*\]\s*$"
    if re.match(pattern, x) is None:
        msg = f"Cannot convert value to list: '{x}'. (with {list_parsing=})"
        output = ValueError(msg)
        return _handle_output(x, handle_exception, output)

    x = re.sub(pattern, r"\1", x)
    if x == "":
        return []  # type: ignore

    x_list = x.split(",")

    output = []
    for xi in x_list:
        output_i = parse_to_type(
            xi, target_item_type, handle_exception="return", **kwds
        )  # type: ignore
        if isinstance(output_i, Exception):
            output = output_i
            break
        output.append(output_i)

    return _handle_output(x, handle_exception, output)


@register_parser_fn(_is_literal_for_parsing)
def _parse_to_literal(
    target_type: TargetType,
    x: str,
    handle_exception: HandleException = "raise",
    **kwds,
) -> Any:
    args = get_args(target_type)
    literal_types = {type(value) for value in args}
    scalar = _parse_to_one_of(tuple(literal_types), target_type, x, **kwds)

    if scalar not in args:
        msg = f"Cannot convert {x} to Literal[{', '.join(args)}]"
        output = ValueError(msg)
    else:
        output = scalar
    return _handle_output(x, handle_exception, output)


@register_parser_fn(_is_optional_for_parsing)
def _parse_to_optional(target_type: TargetType, x: str, **kwds) -> Any:
    args = (NoneType,) + get_args(target_type)
    return _parse_to_one_of(args, target_type, x, **kwds)  # type: ignore


@register_parser_fn(_is_union_for_parsing)
def _parse_to_union(target_type: TargetType, x: str, **kwds) -> Any:
    args = get_args(target_type)
    return _parse_to_one_of(args, target_type, x, **kwds)


def _parse_to_one_of(
    target_types: Iterable[TargetType],
    src_type: TargetType,
    x: str,
    *,
    handle_exception: HandleException = "raise",
    **kwds,
) -> Any:
    def key_fn(xi: Any) -> int:
        if xi is str:
            return 1
        else:
            return 0

    target_types = sorted(target_types, key=key_fn)

    if len(target_types) == 0:
        msg = f"Cannot parse {x}. (expected at least 1 type from {src_type})"
        raise ValueError(msg)

    for target_type in target_types:
        output = parse_to_type(x, target_type, handle_exception="return", **kwds)  # type: ignore
        if not isinstance(output, Exception):
            return _handle_output(x, handle_exception, output)

    msg = f"Invalid argument {x=}. (cannot be parsed to {src_type})"
    output = ValueError(msg)
    return _handle_output(x, handle_exception, output)


def parse_to_optional_bool(
    x: str,
    *,
    case_sensitive: bool = False,
    true_values: Union[str, Iterable[str]] = DEFAULT_TRUE_VALUES,
    false_values: Union[str, Iterable[str]] = DEFAULT_FALSE_VALUES,
    none_values: Union[str, Iterable[str]] = DEFAULT_NONE_VALUES,
    **kwds,
) -> Optional[bool]:
    """Convert string values to optional bool safely. Intended for argparse arguments.

    - True values: 'True', 'T', 'yes', 'y', '1'.
    - False values: 'False', 'F', 'no', 'n', '0'.
    - None values: 'None', 'null'
    - Other raises ValueError.
    """
    return _parse_to_optional(
        Optional[bool],
        x,
        case_sensitive=case_sensitive,
        true_values=true_values,
        false_values=false_values,
        none_values=none_values,
        **kwds,
    )


def parse_to_optional_float(
    x: str,
    *,
    case_sensitive: bool = False,
    none_values: Union[str, Iterable[str]] = DEFAULT_NONE_VALUES,
    **kwds,
) -> Optional[float]:
    """Convert string values to optional float safely. Intended for argparse arguments."""
    return _parse_to_optional(
        Optional[float],
        x,
        case_sensitive=case_sensitive,
        none_values=none_values,
        **kwds,
    )


def parse_to_optional_int(
    x: str,
    *,
    case_sensitive: bool = False,
    none_values: Union[str, Iterable[str]] = DEFAULT_NONE_VALUES,
    **kwds,
) -> Optional[int]:
    """Convert string values to optional int safely. Intended for argparse arguments."""
    return _parse_to_optional(
        Optional[int],
        x,
        case_sensitive=case_sensitive,
        none_values=none_values,
        **kwds,
    )


def parse_to_optional_str(
    x: str,
    *,
    case_sensitive: bool = False,
    none_values: Union[str, Iterable[str]] = DEFAULT_NONE_VALUES,
    **kwds,
) -> Optional[str]:
    """Convert string values to optional str safely. Intended for argparse arguments."""
    return _parse_to_optional(
        Optional[str],
        x,
        case_sensitive=case_sensitive,
        none_values=none_values,
        **kwds,
    )


def _handle_output(x: str, handle_exception: HandleException, output: Any) -> Any:
    if not isinstance(output, Exception):
        return output
    elif handle_exception == "ignore":
        return x  # type: ignore
    elif handle_exception == "raise":
        raise output
    elif handle_exception == "return":
        return output
    else:
        msg = f"Invalid argument {handle_exception=}. (expected one of {get_args(HandleException)})"
        raise ValueError(msg)


def _sanitize_values(values: Union[str, Iterable[str]]) -> List[str]:
    if isinstance(values, str):
        values = [values]
    else:
        values = list(values)
    return values


def _str_in(
    x: str, values: Union[List[str], Tuple[str, ...]], case_sensitive: bool
) -> bool:
    if case_sensitive:
        return x in values
    else:
        return x.lower() in map(str.lower, values)


# ALIASES
@deprecated_alias(get_parse_fn)
def parse_to(*args, **kwds): ...


@deprecated_alias(parse_to_type)
def str_to_type(*args, **kwds): ...


@deprecated_alias(parse_to_bool)
def str_to_bool(*args, **kwds): ...
@deprecated_alias(parse_to_float)
def str_to_float(*args, **kwds): ...
@deprecated_alias(parse_to_int)
def str_to_int(*args, **kwds): ...
@deprecated_alias(parse_to_none)
def str_to_none(*args, **kwds): ...


@deprecated_alias(parse_to_optional_bool)
def str_to_optional_bool(*args, **kwds): ...
@deprecated_alias(parse_to_optional_float)
def str_to_optional_float(*args, **kwds): ...
@deprecated_alias(parse_to_optional_int)
def str_to_optional_int(*args, **kwds): ...
@deprecated_alias(parse_to_optional_str)
def str_to_optional_str(*args, **kwds): ...
