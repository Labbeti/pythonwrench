#!/usr/bin/env python

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Union

from pythonwrench.argparse import parse_args_using_dataclass
from pythonwrench.os import safe_rmdir

logger = logging.getLogger(__name__)


@dataclass
class SafeRmdirArgs:
    root: str = field(metadata={"doc": "Root directory path."})
    rm_root: bool = field(
        default=True,
        metadata={
            "doc": "If True, remove the root directory too if it is empty at the end. defaults to True."
        },
    )
    error_on_non_empty_dir: bool = field(
        default=True,
        metadata={
            "doc": "If True, raises a RuntimeError if a subdirectory contains at least 1 file. Otherwise it will ignore non-empty directories. defaults to True."
        },
    )
    followlinks: bool = field(
        default=False,
        metadata={
            "doc": "Indicates whether or not symbolic links shound be followed. defaults to False."
        },
    )
    dry_run: bool = field(
        default=False,
        metadata={
            "doc": "If True, does not remove any directory and just output the list of directories which could be deleted. defaults to False."
        },
    )
    verbose: int = field(default=0, metadata={"doc": "Verbose level. defaults to 0."})


def main_safe_rmdir() -> None:
    """Perform the main safe rmdir operation."""
    args = parse_args_using_dataclass(SafeRmdirArgs, posonly_for_required=True)
    print_safe_rmdir(
        root=args.root,
        rm_root=args.rm_root,
        error_on_non_empty_dir=args.error_on_non_empty_dir,
        followlinks=args.followlinks,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )


def print_safe_rmdir(
    root: Union[str, Path],
    *,
    rm_root: bool = True,
    error_on_non_empty_dir: bool = True,
    followlinks: bool = False,
    dry_run: bool = False,
    verbose: int = 0,
) -> None:
    """Perform the print safe rmdir operation."""
    deleted, reviewed = safe_rmdir(
        root=root,
        rm_root=rm_root,
        error_on_non_empty_dir=error_on_non_empty_dir,
        followlinks=followlinks,
        dry_run=dry_run,
        verbose=verbose,
    )
    if dry_run:
        msg = f"Dry run mode enabled. Here is the list of directories to delete ({len(deleted)}/{len(reviewed)}):"
        print(msg)
        for path in deleted:
            print(f" - {path}")

    elif verbose >= 1:
        print(f"{len(deleted)} directories has been deleted.")


if __name__ == "__main__":
    main_safe_rmdir()
