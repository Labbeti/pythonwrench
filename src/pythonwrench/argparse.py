#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import partial
from typing import (
    Any,
    Callable,
    Iterable,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

from pythonwrench.typing.classes import NoneType

T = TypeVar("T")


DEFAULT_TRUE_VALUES = ("True", "t", "yes", "y", "1")
DEFAULT_FALSE_VALUES = ("False", "f", "no", "n", "0")
DEFAULT_NONE_VALUES = ("None", "null")


def parse_to(
    target_type: Type[T],
    *,
    case_sensitive: bool = False,
    true_values: Union[str, Iterable[str]] = DEFAULT_TRUE_VALUES,
    false_values: Union[str, Iterable[str]] = DEFAULT_FALSE_VALUES,
    none_values: Union[str, Iterable[str]] = DEFAULT_NONE_VALUES,
) -> Callable[[str], T]:
    """Returns a callable that convert string value to target type safely.

    Intended for argparse arguments.
    """
    return partial(
        str_to_type,
        target_type=target_type,
        case_sensitive=case_sensitive,
        true_values=true_values,
        false_values=false_values,
        none_values=none_values,
    )


def str_to_type(
    x: str,
    target_type: Type[T],
    *,
    case_sensitive: bool = False,
    true_values: Union[str, Iterable[str]] = DEFAULT_TRUE_VALUES,
    false_values: Union[str, Iterable[str]] = DEFAULT_FALSE_VALUES,
    none_values: Union[str, Iterable[str]] = DEFAULT_NONE_VALUES,
) -> T:
    """Convert string values to target type safely. Intended for argparse arguments.

    - True values: 'True', 'T', 'yes', 'y', '1'.
    - False values: 'False', 'F', 'no', 'n', '0'.
    - None values: 'None', 'null'
    - Other raises ValueError.
    """
    result = _str_to_type_impl(
        x,
        target_type,
        case_sensitive=case_sensitive,
        true_values=true_values,
        false_values=false_values,
        none_values=none_values,
    )
    if isinstance(result, Exception):
        raise result
    else:
        return result


def str_to_bool(
    x: str,
    *,
    case_sensitive: bool = False,
    true_values: Union[str, Iterable[str]] = DEFAULT_TRUE_VALUES,
    false_values: Union[str, Iterable[str]] = DEFAULT_FALSE_VALUES,
) -> bool:
    """Convert string values to bool safely. Intended for argparse arguments.

    - True values: 'True', 'T', 'yes', 'y', '1'.
    - False values: 'False', 'F', 'no', 'n', '0'.
    - Other raises ValueError.
    """
    return str_to_type(
        x,
        bool,
        case_sensitive=case_sensitive,
        true_values=true_values,
        false_values=false_values,
    )


def str_to_none(
    x: str,
    *,
    case_sensitive: bool = False,
    none_values: Union[str, Iterable[str]] = DEFAULT_NONE_VALUES,
) -> None:
    """Convert string values to None safely. Intended for argparse arguments.

    - None values: 'None', 'null'
    - Other raises ValueError.
    """
    return str_to_type(
        x, NoneType, case_sensitive=case_sensitive, none_values=none_values
    )


def str_to_optional_bool(
    x: str,
    *,
    case_sensitive: bool = False,
    true_values: Union[str, Iterable[str]] = DEFAULT_TRUE_VALUES,
    false_values: Union[str, Iterable[str]] = DEFAULT_FALSE_VALUES,
    none_values: Union[str, Iterable[str]] = DEFAULT_NONE_VALUES,
) -> Optional[bool]:
    """Convert string values to optional bool safely. Intended for argparse arguments.

    - True values: 'True', 'T', 'yes', 'y', '1'.
    - False values: 'False', 'F', 'no', 'n', '0'.
    - None values: 'None', 'null'
    - Other raises ValueError.
    """
    return str_to_type(
        x, Optional[bool], case_sensitive=case_sensitive, none_values=none_values
    )


def str_to_optional_float(
    x: str,
    *,
    case_sensitive: bool = False,
    none_values: Union[str, Iterable[str]] = DEFAULT_NONE_VALUES,
) -> Optional[float]:
    """Convert string values to optional float safely. Intended for argparse arguments."""
    return str_to_type(
        x, Optional[float], case_sensitive=case_sensitive, none_values=none_values
    )


def str_to_optional_int(
    x: str,
    *,
    case_sensitive: bool = False,
    none_values: Union[str, Iterable[str]] = DEFAULT_NONE_VALUES,
) -> Optional[int]:
    """Convert string values to optional int safely. Intended for argparse arguments."""
    return str_to_type(
        x, Optional[int], case_sensitive=case_sensitive, none_values=none_values
    )


def str_to_optional_str(
    x: str,
    *,
    case_sensitive: bool = False,
    none_values: Union[str, Iterable[str]] = DEFAULT_NONE_VALUES,
) -> Optional[str]:
    """Convert string values to optional str safely. Intended for argparse arguments."""
    return str_to_type(
        x, Optional[str], case_sensitive=case_sensitive, none_values=none_values
    )


def _str_to_type_impl(
    x: str,
    target_type: Type[T],
    *,
    case_sensitive: bool = False,
    true_values: Union[str, Iterable[str]] = DEFAULT_TRUE_VALUES,
    false_values: Union[str, Iterable[str]] = DEFAULT_FALSE_VALUES,
    none_values: Union[str, Iterable[str]] = DEFAULT_NONE_VALUES,
) -> Union[T, Exception]:
    if target_type in (str, int, float, None, NoneType, bool):
        return _str_to_scalar_impl(
            x,
            target_type,
            case_sensitive=case_sensitive,
            true_values=true_values,
            false_values=false_values,
            none_values=none_values,
        )

    origin = get_origin(target_type)
    if getattr(target_type, "__name__", None) == "Optional":
        args = (None,) + get_args(target_type)
    elif origin == Union or origin.__name__ in ("Union", "UnionType"):  # type: ignore
        args = get_args(target_type)
    else:
        msg = f"Invalid argument {target_type=}. (unsupported type)"
        raise ValueError(msg)

    # str is always at the end
    def key_fn(xi: Any) -> int:
        if xi is str:
            return 1
        else:
            return 0

    args = sorted(args, key=key_fn)

    for arg in args:
        result = _str_to_type_impl(
            x,
            arg,  # type: ignore
            case_sensitive=case_sensitive,
            true_values=true_values,
            false_values=false_values,
        )
        if not isinstance(result, Exception):
            return result

    return ValueError(f"Invalid argument {x=} with {target_type=}.")


def _str_to_scalar_impl(
    x: str,
    target_type: Type[T],
    *,
    case_sensitive: bool = False,
    true_values: Union[str, Iterable[str]] = DEFAULT_TRUE_VALUES,
    false_values: Union[str, Iterable[str]] = DEFAULT_FALSE_VALUES,
    none_values: Union[str, Iterable[str]] = DEFAULT_NONE_VALUES,
) -> Any:
    if target_type is str:
        return x
    elif target_type is int:
        try:
            return int(x)
        except ValueError as err:
            return err
    elif target_type is float:
        try:
            return float(x)
        except ValueError as err:
            return err
    elif target_type in (None, NoneType):
        return _str_to_none_impl(
            x, case_sensitive=case_sensitive, none_values=none_values
        )
    elif target_type is bool:
        return _str_to_bool_impl(
            x,
            case_sensitive=case_sensitive,
            true_values=true_values,
            false_values=false_values,
        )
    else:
        raise ValueError(f"Invalid argument {target_type=}. (unsupported type)")


def _str_to_bool_impl(
    x: str,
    *,
    case_sensitive: bool = False,
    true_values: Union[str, Iterable[str]] = DEFAULT_TRUE_VALUES,
    false_values: Union[str, Iterable[str]] = DEFAULT_FALSE_VALUES,
) -> Union[bool, Exception]:
    true_values = _sanitize_values(true_values)
    if _str_in(x, true_values, case_sensitive):
        return True

    false_values = _sanitize_values(false_values)
    if _str_in(x, false_values, case_sensitive):
        return False

    values = tuple(true_values + false_values)
    err = ValueError(f"Invalid argument '{x}'. (expected one of {values})")
    return err


def _str_to_none_impl(
    x: str,
    *,
    case_sensitive: bool = False,
    none_values: Union[str, Iterable[str]] = DEFAULT_NONE_VALUES,
) -> Union[None, Exception]:
    """Convert string values to None safely. Intended for argparse arguments.

    - None values: 'None', 'null'
    - Other raises ValueError.
    """
    none_values = _sanitize_values(none_values)
    if _str_in(x, none_values, case_sensitive):
        return None

    values = tuple(none_values)
    err = ValueError(f"Invalid argument '{x}'. (expected one of {values})")
    return err


def _sanitize_values(values: Union[str, Iterable[str]]) -> List[str]:
    if isinstance(values, str):
        values = [values]
    else:
        values = list(values)
    return values


def _str_in(x: str, values: List[str], case_sensitive: bool) -> bool:
    if case_sensitive:
        return x in values
    else:
        return x.lower() in map(str.lower, values)
