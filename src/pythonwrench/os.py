#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import os.path as osp
import sys
from pathlib import Path
from re import Pattern
from typing import Any, Generator, Iterable, List, Tuple, Union

from pythonwrench.re import PatternLike, compile_patterns, match_patterns
from pythonwrench.warnings import warn_once

logger = logging.getLogger(__name__)


def get_num_cpus_available() -> int:
    """Returns the number of CPUs available for the current process on Linux-based platforms.

    On Windows and MAC OS, this will just return the number of logical CPUs on this machine.
    If the number of CPUs cannot be detected, returns 0.
    """
    try:
        num_cpus = len(os.sched_getaffinity(0))
    except AttributeError:
        msg = "Cannot detect number of CPUs available for the current process. This function will just returns the number of CPUs on this machine."
        warn_once(msg)

        num_cpus = os.cpu_count()
        if num_cpus is None:
            num_cpus = 0
    return num_cpus


def safe_rmdir(
    root: Union[str, Path],
    *,
    rm_root: bool = True,
    error_on_non_empty_dir: bool = True,
    followlinks: bool = False,
    dry_run: bool = False,
    verbose: int = 0,
) -> Tuple[List[str], List[str]]:
    """Remove all empty sub-directories.

    Args:
        root: Root directory path.
        rm_root: If True, remove the root directory too if it is empty at the end. defaults to True.
        error_on_non_empty_dir: If True, raises a RuntimeError if a subdirectory contains at least 1 file. Otherwise it will ignore non-empty directories. defaults to True.
        followlinks: Indicates whether or not symbolic links shound be followed. defaults to False.
        dry_run: If True, does not remove any directory and just output the list of directories which could be deleted. defaults to False.
        verbose: Verbose level. defaults to 0.

    Returns:
        A tuple containing the list of directories paths deleted and the list of directories paths reviewed.
    """
    root = str(root)
    if not osp.isdir(root):
        msg = f"Target root directory does not exists. (with {root=})"
        raise FileNotFoundError(msg)

    to_delete = {}
    reviewed = []
    walker = os.walk(root, topdown=False, followlinks=followlinks)

    for dpath, dnames, fnames in walker:
        reviewed.append(dpath)

        if not rm_root and dpath == root:
            continue

        elif len(fnames) == 0 and (
            all(osp.join(dpath, dname) in to_delete for dname in dnames)
        ):
            to_delete[dpath] = None

        elif error_on_non_empty_dir:
            raise RuntimeError(f"Cannot remove non-empty directory '{dpath}'.")
        elif verbose >= 2:
            logger.debug(f"Ignoring non-empty directory '{dpath}'...")

    if not dry_run:
        for dpath in to_delete:
            os.rmdir(dpath)

    return list(to_delete), reviewed


def tree_iter(
    root: Union[str, Path],
    *,
    include: Union[PatternLike, Iterable[PatternLike]] = ".*",
    exclude: Union[PatternLike, Iterable[PatternLike]] = (),
    space: str = "    ",
    branch: str = "│   ",
    tee: str = "├── ",
    last: str = "└── ",
    max_depth: int = sys.maxsize,
    followlinks: bool = False,
    skipfiles: bool = False,
    sort: bool = False,
) -> Generator[str, Any, None]:
    """A recursive generator, given a directory Path object will yield a visual tree structure line by line with each line prefixed by the same characters

    Based on: https://stackoverflow.com/questions/9727673/list-directory-tree-structure-in-python
    """
    root = Path(root)
    if not root.is_dir():
        msg = f"Invalid argument path '{root}'. (not a directory)"
        raise ValueError(msg)

    if not followlinks and root.is_symlink():
        yield from ()
        return

    include = compile_patterns(include)
    exclude = compile_patterns(exclude)
    if not match_patterns(str(root), include, exclude=exclude):
        yield from ()
        return

    yield root.resolve().name + "/"

    if max_depth <= 0:
        return

    yield from _tree_impl(
        root,
        include=include,
        exclude=exclude,
        prefix="",
        space=space,
        branch=branch,
        tee=tee,
        last=last,
        max_depth=max_depth,
        followlinks=followlinks,
        skipfiles=skipfiles,
        sort=sort,
    )


def _tree_impl(
    root: Path,
    *,
    include: List[Pattern],
    exclude: List[Pattern],
    max_depth: int,
    followlinks: bool,
    skipfiles: bool,
    sort: bool,
    prefix: str,
    space: str,
    branch: str,
    tee: str,
    last: str,
) -> Generator[str, Any, None]:
    walker = _walker_impl(
        root,
        [],
        include=include,
        exclude=exclude,
        max_depth=max_depth,
        followlinks=followlinks,
        skipfiles=skipfiles,
        sort=sort,
    )
    for path, is_dir, locs in walker:
        prefix = "".join((branch if i < num - 1 else space) for i, num in locs[:-1])
        index_in_parent, num_files_in_parent = locs[-1]
        pointer = tee if index_in_parent < num_files_in_parent - 1 else last
        suffix = "/" if is_dir else ""

        yield prefix + pointer + path.name + suffix


def _walker_impl(
    root: Path,
    locs: List[Tuple[int, int]],
    *,
    include: List[Pattern],
    exclude: List[Pattern],
    max_depth: int,
    followlinks: bool,
    skipfiles: bool,
    sort: bool,
) -> Generator[Tuple[Path, bool, List[Tuple[int, int]]], Any, None]:
    candidates_paths = root.iterdir()

    if sort:
        candidates_paths = sorted(candidates_paths)

    paths: List[Path] = []
    for path in candidates_paths:
        if not match_patterns(str(path), include, exclude=exclude):
            continue

        try:
            if not followlinks and path.is_symlink():
                continue
            if skipfiles and path.is_file():
                continue

            paths.append(path)
        except PermissionError:
            pass

    for i, path in enumerate(paths):
        is_dir = path.is_dir()
        locs_i = locs + [(i, len(paths))]
        yield path, is_dir, locs_i

        if is_dir and len(locs_i) < max_depth:
            yield from _walker_impl(
                path,
                locs=locs_i,
                include=include,
                exclude=exclude,
                max_depth=max_depth,
                followlinks=followlinks,
                skipfiles=skipfiles,
                sort=sort,
            )
