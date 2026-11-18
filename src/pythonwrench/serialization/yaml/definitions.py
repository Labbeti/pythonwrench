#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Type, Union

from typing_extensions import TypeAlias

from pythonwrench.importlib import is_available_package


def yaml_is_available() -> bool:
    return is_available_package("yaml")


if not yaml_is_available():
    from . import _yaml_fallback as yaml
    from ._yaml_fallback import (
        BaseLoader,
        CBaseLoader,
        CFullLoader,
        CLoader,
        CSafeLoader,
        CUnsafeLoader,
        FullLoader,
        Loader,
        MappingNode,
        Node,
        ParserError,
        SafeLoader,
        ScalarNode,
        ScannerError,
        SequenceNode,
        UnsafeLoader,
    )

else:
    import yaml  # noqa: F401
    from yaml import (  # noqa: F401
        BaseLoader,
        FullLoader,
        Loader,
        MappingNode,
        Node,
        SafeLoader,
        ScalarNode,
        SequenceNode,
        UnsafeLoader,
    )
    from yaml.parser import ParserError  # noqa: F401
    from yaml.scanner import ScannerError  # noqa: F401

    try:
        from yaml import (
            CBaseLoader,
            CFullLoader,
            CLoader,
            CSafeLoader,
            CUnsafeLoader,
        )
    except ImportError:
        from ._yaml_fallback import (
            CBaseLoader,
            CFullLoader,
            CLoader,
            CSafeLoader,
            CUnsafeLoader,
        )


YamlLoaders: TypeAlias = Union[
    Type[Loader],
    Type[BaseLoader],
    Type[FullLoader],
    Type[SafeLoader],
    Type[UnsafeLoader],
    Type[CLoader],
    Type[CBaseLoader],
    Type[CFullLoader],
    Type[CSafeLoader],
    Type[CUnsafeLoader],
]
