#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import TYPE_CHECKING

try:
    import lazy_loader as lazy  # type: ignore
except ImportError:
    lazy = None


if TYPE_CHECKING or lazy is None:
    from . import definitions as definitions
    from . import func as func
    from .definitions import YamlLoaders, yaml, yaml_is_available
    from .func import (
        IgnoreTagLoader,
        SafeLoader,
        SplitTagLoader,
        dump_yaml,
        dumps_yaml,
        load_yaml,
        loads_yaml,
        read_yaml,
        save_yaml,
    )

else:
    __getattr__, __dir__, __all__ = lazy.attach(
        __name__,
        submodules=["definitions", "func"],
        submod_attrs={
            "definitions": ["YamlLoaders", "func", "yaml_is_available"],
            "func": [
                "IgnoreTagLoader",
                "SafeLoader",
                "SplitTagLoader",
                "dump_yaml",
                "dumps_yaml",
                "load_yaml",
                "loads_yaml",
                "read_yaml",
                "save_yaml",
            ],
        },
    )

del TYPE_CHECKING
