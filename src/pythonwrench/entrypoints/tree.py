#!/usr/bin/env python

import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Union

from pythonwrench.argparse import parse_args_using_dataclass
from pythonwrench.os import tree_iter
from pythonwrench.re import PatternListLike

logger = logging.getLogger(__name__)


@dataclass
class TreeArgs:
    root: str = field(default=".", metadata={"doc": "Root directory path."})
    include: List[str] = field(
        default_factory=lambda: [".*"], metadata={"doc": "Include file/dir patterns."}
    )
    exclude: List[str] = field(
        default_factory=list, metadata={"doc": "Exclude file/dir patterns."}
    )
    max_depth: int = field(
        default=sys.maxsize, metadata={"doc": "Max directory tree depth."}
    )
    followlinks: bool = field(
        default=True,
        metadata={
            "doc": "Indicates whether or not symbolic links should be followed. defaults to True."
        },
    )
    skipfiles: bool = field(
        default=False,
        metadata={
            "doc": "Indicates whether or not symbolic files should be shown. defaults to False."
        },
    )
    sort: bool = field(
        default=False, metadata={"doc": "Sort element by name. defaults to False."}
    )


def main_tree() -> None:
    """Perform the main tree operation."""
    args = parse_args_using_dataclass(TreeArgs, positionals=["root"])
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
    include: PatternListLike = ".*",
    exclude: PatternListLike = (),
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
