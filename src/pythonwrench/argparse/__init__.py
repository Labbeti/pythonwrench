#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import TYPE_CHECKING

try:
    import lazy_loader as lazy  # type: ignore
except ImportError:
    lazy = None


if TYPE_CHECKING or lazy is None:
    from . import dataclass_ as dataclass_
    from . import parsers as parsers
    from .dataclass_ import (
        add_dataclass_fields_to_parser,
        new_parser_from_dataclass,
        parse_args_using_dataclass,
    )
    from .parsers import (
        get_parse_fn,
        parse_to,
        parse_to_bool,
        parse_to_float,
        parse_to_int,
        parse_to_none,
        parse_to_optional_bool,
        parse_to_optional_float,
        parse_to_optional_int,
        parse_to_optional_str,
        parse_to_type,
        register_parser_fn,
        str_to_bool,
        str_to_float,
        str_to_int,
        str_to_none,
        str_to_optional_bool,
        str_to_optional_float,
        str_to_optional_int,
        str_to_optional_str,
        str_to_type,
    )

else:
    __getattr__, __dir__, __all__ = lazy.attach(
        __name__,
        submodules=["dataclass_", "parsers"],
        submod_attrs={
            "dataclass_": [
                "add_dataclass_fields_to_parser",
                "new_parser_from_dataclass",
                "parse_args_using_dataclass",
            ],
            "parsers": [
                "get_parse_fn",
                "parse_to",
                "parse_to_bool",
                "parse_to_float",
                "parse_to_int",
                "parse_to_none",
                "parse_to_optional_bool",
                "parse_to_optional_float",
                "parse_to_optional_int",
                "parse_to_optional_str",
                "parse_to_type",
                "register_parser_fn",
                "str_to_bool",
                "str_to_float",
                "str_to_int",
                "str_to_none",
                "str_to_optional_bool",
                "str_to_optional_float",
                "str_to_optional_int",
                "str_to_optional_str",
                "str_to_type",
            ],
        },
    )


del TYPE_CHECKING, lazy
