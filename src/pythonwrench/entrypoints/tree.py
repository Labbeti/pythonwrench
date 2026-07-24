#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Iterable, Union

from pythonwrench.argparse import str_to_bool
from pythonwrench.os import tree_iter
from pythonwrench.re import PatternLike

logger = logging.getLogger(__name__)


def main_tree() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "root",
        type=str,
        help="Root directory path.",
        default=".",
        nargs="?",  # for optional positional argument
    )
    parser.add_argument(
        "--include",
        type=str,
        help="Include file/dir patterns.",
        default=".*",
        nargs="*",
    )
    parser.add_argument(
        "--exclude",
        type=str,
        help="Exclude file/dir patterns.",
        default=(),
        nargs="*",
    )
    parser.add_argument(
        "--max_depth",
        type=int,
        help="Max directory tree depth.",
        default=sys.maxsize,
    )
    parser.add_argument(
        "--followlinks",
        type=str_to_bool,
        help="Indicates whether or not symbolic links should be followed. defaults to True.",
        default=True,
    )
    parser.add_argument(
        "--skipfiles",
        type=str_to_bool,
        help="Indicates whether or not symbolic files should be shown. defaults to False.",
        default=False,
    )
    parser.add_argument(
        "--sort",
        type=str_to_bool,
        help="Sort element by name. defaults to False.",
        default=False,
    )
    args = parser.parse_args()

    print_tree(
        root=args.root,
        include=args.include,
        exclude=args.exclude,
        max_depth=args.max_depth,
        followlinks=args.followlinks,
        skipfiles=args.skipfiles,
        sort=args.sort,
    )


def print_tree(
    root: Union[str, Path],
    *,
    include: Union[PatternLike, Iterable[PatternLike]] = ".*",
    exclude: Union[PatternLike, Iterable[PatternLike]] = (),
    max_depth: int = sys.maxsize,
    followlinks: bool = False,
    skipfiles: bool = False,
    sort: bool = False,
) -> None:
    """Print directory tree to stdout."""
    num_dirs = 0
    num_files = 0

    iterable = tree_iter(
        root=root,
        include=include,
        exclude=exclude,
        max_depth=max_depth,
        followlinks=followlinks,
        skipfiles=skipfiles,
        sort=sort,
    )
    for line in iterable:
        print(f"{line}")

        if line.endswith("/"):
            num_dirs += 1
        else:
            num_files += 1

    print(f"\n{num_dirs} directories, {num_files} files")


if __name__ == "__main__":
    main_tree()
