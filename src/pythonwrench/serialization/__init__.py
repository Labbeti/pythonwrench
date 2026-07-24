#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import TYPE_CHECKING

try:
    import lazy_loader as lazy  # type: ignore
except ImportError:
    lazy = None


if TYPE_CHECKING or lazy is None:
    from .csv import dump_csv, dumps_csv, load_csv, loads_csv, read_csv, save_csv
    from .json import dump_json, dumps_json, load_json, loads_json, read_json, save_json
    from .jsonl import (
        dump_jsonl,
        dumps_jsonl,
        load_jsonl,
        loads_jsonl,
        read_jsonl,
        save_jsonl,
    )
    from .pickle import (
        dump_pickle,
        dumps_pickle,
        load_pickle,
        loads_pickle,
        read_pickle,
        save_pickle,
    )

else:
    __getattr__, __dir__, __all__ = lazy.attach(
        __name__,
        submodules=["csv", "json", "jsonl", "pickle"],
        submod_attrs={
            "csv": [
                "dump_csv",
                "dumps_csv",
                "load_csv",
                "loads_csv",
                "read_csv",
                "save_csv",
            ],
            "json": [
                "dump_json",
                "dumps_json",
                "load_json",
                "loads_json",
                "read_json",
                "save_json",
            ],
            "jsonl": [
                "dump_jsonl",
                "dumps_jsonl",
                "load_jsonl",
                "loads_jsonl",
                "read_jsonl",
                "save_jsonl",
            ],
            "pickle": [
                "dump_pickle",
                "dumps_pickle",
                "load_pickle",
                "loads_pickle",
                "read_pickle",
                "save_pickle",
            ],
        },
    )
