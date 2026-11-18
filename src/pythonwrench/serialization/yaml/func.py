#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
from argparse import Namespace
from pathlib import Path
from typing import Any, Iterable, Literal, Mapping, Optional, Union

from pythonwrench.cast import as_builtin
from pythonwrench.functools import function_alias
from pythonwrench.importlib import requires_packages
from pythonwrench.serialization._core import (
    OnError,
    _dump_base,
    _load_base,
    _loads_base,
)
from pythonwrench.serialization.yaml.definitions import (
    MappingNode,
    Node,
    ParserError,
    SafeLoader,
    ScalarNode,
    ScannerError,
    SequenceNode,
    YamlLoaders,
    yaml,
    yaml_is_available,
)
from pythonwrench.typing import DataclassInstance, NamedTupleInstance


@requires_packages("yaml")
def dump_yaml(
    data: Union[
        Iterable[Any],
        Mapping[str, Any],
        Namespace,
        DataclassInstance,
        NamedTupleInstance,
    ],
    target: Union[str, Path, None] = None,
    *,
    overwrite: bool = True,
    to_builtins: bool = False,
    make_parents: bool = True,
    encoding: Optional[str] = "utf-8",
    # YAML dump kwargs
    sort_keys: bool = False,
    indent: Union[int, None] = None,
    width: Union[int, None] = 1000,
    allow_unicode: bool = True,
    **yaml_dump_kwds,
) -> str:
    """Dump content to YAML format."""
    return _dump_base(
        _serialize_yaml,
        "text",
        data,
        target,
        overwrite=overwrite,
        to_builtins=to_builtins,
        make_parents=make_parents,
        encoding=encoding,
        sort_keys=sort_keys,
        indent=indent,
        width=width,
        allow_unicode=allow_unicode,
        **yaml_dump_kwds,
    )


@function_alias(dump_yaml)
def dumps_yaml(*args, **kwargs): ...


@function_alias(dump_yaml)
def save_yaml(*args, **kwargs): ...


@requires_packages("yaml")
def load_yaml(
    source: Union[str, Path, io.TextIOBase],
    /,
    *,
    Loader: YamlLoaders = SafeLoader,
    on_error: Literal["raise", "ignore"] = "raise",
) -> Any:
    """Load YAML from filepath or opened file."""
    return _load_base(
        _parse_yaml,
        "text",
        source,
        on_error=on_error,
        Loader=Loader,
    )


@requires_packages("yaml")
def loads_yaml(
    source: str,
    /,
    *,
    on_error: OnError = "raise",
    Loader: YamlLoaders = SafeLoader,
) -> Any:
    """Load YAML from string and text-io stream."""
    return _loads_base(
        _parse_yaml,
        "text",
        source,
        on_error=on_error,
        Loader=Loader,
    )


@function_alias(load_yaml)
def read_yaml(*args, **kwargs): ...


def _serialize_yaml(
    data: Union[
        Iterable[Any],
        Mapping[str, Any],
        Namespace,
        DataclassInstance,
        NamedTupleInstance,
    ],
    target: io.TextIOBase,
    *,
    to_builtins: bool = False,
    encoding: Optional[str] = "utf-8",
    # YAML dump kwargs
    sort_keys: bool = False,
    indent: Union[int, None] = None,
    width: Union[int, None] = 1000,
    allow_unicode: bool = True,
    **yaml_dump_kwds,
) -> None:
    if to_builtins:
        data = as_builtin(data)

    content = yaml.dump(
        data,
        target,
        sort_keys=sort_keys,
        indent=indent,
        width=width,
        allow_unicode=allow_unicode,
        encoding=encoding,
        **yaml_dump_kwds,
    )
    return content


def _parse_yaml(
    source: Union[str, io.TextIOBase],
    *,
    on_error: OnError,
    default: Any,
    Loader: YamlLoaders = SafeLoader,
) -> Any:
    try:
        return yaml.load(source, Loader=Loader)  # type: ignore
    except (ScannerError, ParserError):
        if on_error == "ignore":
            return default
        else:
            raise


class IgnoreTagLoader(SafeLoader):  # type: ignore
    r"""SafeLoader that ignores yaml tags.

    Examples
    ========

    ```python
    >>> dumped = "a: !!python/tuple\n- 1\n- 2"
    >>> yaml.load(dumped, Loader=IgnoreTagLoader)
    ... {"a": [1, 2]}
    >>> yaml.load(dumped, Loader=FullLoader)
    ... {"a": (1, 2)}
    >>> yaml.load(dumped, Loader=SafeLoader)  # raises ConstructorError
    ```
    """

    def construct_with_tag(self, tag: str, node: Node) -> Any:
        if isinstance(node, MappingNode):
            return self.construct_mapping(node)
        elif isinstance(node, ScalarNode):
            return self.construct_scalar(node)
        elif isinstance(node, SequenceNode):
            return self.construct_sequence(node)
        else:
            msg = f"Unsupported node type {type(node)} with {tag=}."
            raise NotImplementedError(msg)


class SplitTagLoader(SafeLoader):  # type: ignore
    r"""SafeLoader that store tags inside value.

    Examples
    ========

    ```python
    >>> dumped = "a: !!python/tuple\n- 1\n- 2"
    >>> yaml.load(dumped, Loader=SplitTagLoader)
    ... {'a': {'_target_': 'yaml.org,2002:python/tuple', '_args_': [1, 2]}}
    ```
    """

    def __init__(
        self,
        stream,
        *,
        tag_key: str = "_target_",
        args_key: str = "_args_",
    ) -> None:
        super().__init__(stream)
        self.tag_key = tag_key
        self.args_key = args_key

    def construct_with_tag(self, tag: str, node: Node) -> Any:
        if isinstance(node, MappingNode):
            result = self.construct_mapping(node)
        elif isinstance(node, ScalarNode):
            result = self.construct_scalar(node)
        elif isinstance(node, SequenceNode):
            result = self.construct_sequence(node)
        else:
            msg = f"Unsupported node type {type(node)} with {tag=}."
            raise NotImplementedError(msg)

        result = {
            self.tag_key: tag,
            self.args_key: result,
        }
        return result


if yaml_is_available():
    IgnoreTagLoader.add_multi_constructor("!", IgnoreTagLoader.construct_with_tag)  # type: ignore
    IgnoreTagLoader.add_multi_constructor("tag:", IgnoreTagLoader.construct_with_tag)  # type: ignore

    SplitTagLoader.add_multi_constructor("!", SplitTagLoader.construct_with_tag)  # type: ignore
    SplitTagLoader.add_multi_constructor("tag:", SplitTagLoader.construct_with_tag)  # type: ignore
