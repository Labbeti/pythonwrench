#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import re
from functools import partial
from re import Pattern
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    Mapping,
    Optional,
    Tuple,
    TypeVar,
    Union,
    get_args,
    overload,
)

from typing_extensions import TypeAlias

from pythonwrench.collections.collections import DictByKV, K, V, find
from pythonwrench.warnings import deprecated_alias

T = TypeVar("T")

PatternLike: TypeAlias = Union[str, Pattern]
PatternListLike: TypeAlias = Union[PatternLike, Iterable[PatternLike]]

MatchFn = Callable[[PatternLike, str], Any]
MatchName = Literal["search", "match"]
MatchLike = Union[MatchFn, MatchName]

logger = logging.getLogger(__name__)


def filter_iter_with_patterns(
    x: Iterable[str],
    include: Optional[PatternListLike] = ".*",
    *,
    exclude: Optional[PatternListLike] = (),
    match_fn: MatchLike = re.search,
) -> List[str]:
    """Perform the filter with patterns operation."""
    if include is None:
        include = ".*"
    if exclude is None:
        exclude = ()

    return [
        xi
        for xi in x
        if match_patterns(xi, include, exclude=exclude, match_fn=match_fn)
    ]


@deprecated_alias(filter_iter_with_patterns)
def filter_with_patterns(*args, **kwargs): ...


@overload
def filter_dict_with_patterns(
    x: Mapping[str, V],
    include: Optional[PatternListLike] = ".*",
    *,
    by: Literal["key"] = "key",
    exclude: Optional[PatternListLike] = (),
    match_fn: MatchLike = re.search,
) -> Dict[str, V]: ...


@overload
def filter_dict_with_patterns(
    x: Mapping[K, str],
    include: Optional[PatternListLike] = ".*",
    *,
    by: Literal["value"],
    exclude: Optional[PatternListLike] = (),
    match_fn: MatchLike = re.search,
) -> Dict[K, str]: ...


def filter_dict_with_patterns(
    x: Mapping[K, V],
    include: Optional[PatternListLike] = ".*",
    *,
    by: DictByKV = "key",
    exclude: Optional[PatternListLike] = (),
    match_fn: MatchLike = re.search,
) -> Dict[K, V]:
    """Perform the filter with patterns operation."""
    if by == "key":

        def predicate(item: Tuple[K, V]) -> bool:
            return match_patterns(item[0], include, exclude=exclude, match_fn=match_fn)  # type: ignore[assignment]

    elif by == "value":

        def predicate(item: Tuple[K, V]) -> bool:
            return match_patterns(item[1], include, exclude=exclude, match_fn=match_fn)  # type: ignore[assignment]

    else:
        msg = f"Invalid argument {by=}. (expected one of {get_args(DictByKV)})"
        raise ValueError(msg)

    return {k: v for k, v in x.items() if predicate((k, v))}


def match_patterns(
    x: str,
    include: Optional[PatternListLike] = ".*",
    *,
    exclude: Optional[PatternListLike] = (),
    match_fn: MatchLike = re.search,
) -> bool:
    """Returns True if the first argument match at least 1 included pattern and does not match any excluded pattern.

    Args:
        x: String to check.
        include: Acceptable pattern(s) for x. If None, match all patterns with '.*'. defaults to '.*'.
        exclude: Forbidden pattern(s) for x. If None, match no patterns with value (). defaults to ().
        match_fn: Match function use to compare a pattern with argument x. defaults to re.search.
    """
    if include is None:
        include = ".*"
    if exclude is None:
        exclude = ()

    include_index = find_patterns(x, include, match_fn=match_fn, default=-1)
    exclude_index = find_patterns(x, exclude, match_fn=match_fn, default=-1)
    return include_index != -1 and exclude_index == -1


def sort_with_patterns(
    x: Iterable[str],
    patterns: PatternListLike,
    *,
    match_fn: MatchLike = re.search,
    reverse: bool = False,
) -> List[str]:
    """Perform the sort with patterns operation."""
    key_fn = get_key_fn(patterns, match_fn=match_fn)
    x = sorted(x, key=key_fn, reverse=reverse)
    return x


def get_key_fn(
    patterns: PatternListLike,
    *,
    match_fn: MatchLike = re.search,
) -> Callable[[str], int]:
    """Generate key_fn to sorted list of string using multiple patterns.

    Example
    -------
    >>> lst = ["a", "abc", "aa", "abcd"]
    >>> patterns = ["^ab"]  # sort list with elements starting with 'ab' first
    >>> list(sorted(lst, key=get_key_fn(patterns)))
    ... ["abc", "abcd", "a", "aa"]
    """
    patterns = compile_patterns(patterns)
    key_fn = partial(
        find_patterns,
        patterns=patterns,
        match_fn=match_fn,
        default=len(patterns),
    )
    return key_fn  # type: ignore


def find_patterns(
    x: str,
    patterns: PatternListLike,
    *,
    match_fn: MatchLike = re.search,
    default: T = -1,
) -> Union[int, T]:
    """Find index of a pattern that match the first argument. If no pattern matches, returns the default value (-1)."""
    patterns = compile_patterns(patterns)
    match_fn = _get_match_fn(match_fn)
    index = find(x, patterns, match_fn=match_fn, order="right", default=default)
    return index


def compile_patterns(patterns: PatternListLike) -> List[Pattern]:
    """Compile patterns-like to a list."""
    if isinstance(patterns, (str, Pattern)):
        patterns = [patterns]
    patterns = [re.compile(pattern) for pattern in patterns]
    return patterns


def _get_match_fn(match_fn: MatchLike) -> MatchFn:
    if callable(match_fn):
        return match_fn
    elif match_fn == "search":
        return re.search
    elif match_fn == "match":
        return re.match
    else:
        msg = f"Invalid argument {match_fn=}. (expected callable, 'search' or 'match')"
        raise ValueError(msg)
