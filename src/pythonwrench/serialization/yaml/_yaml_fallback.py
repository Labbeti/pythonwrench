#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pythonwrench.importlib import Placeholder
from pythonwrench.inspect import get_current_fn_name


class BaseLoader(Placeholder): ...


class CBaseLoader(Placeholder): ...


class CFullLoader(Placeholder): ...


class CLoader(Placeholder): ...


class CSafeLoader(Placeholder): ...


class CUnsafeLoader(Placeholder): ...


class FullLoader(Placeholder): ...


class Loader(Placeholder): ...


class MappingNode(Placeholder): ...


class Node(Placeholder): ...


class SafeLoader(Placeholder): ...


class ScalarNode(Placeholder): ...


class SequenceNode(Placeholder): ...


class UnsafeLoader(Placeholder): ...


class ParserError(RuntimeError): ...


class ScannerError(RuntimeError): ...


def load(*args, **kwargs):
    msg = f"Cannot call function '{get_current_fn_name()}' because optional dependency 'pyyaml' is not installed. Please install it using 'pip install torchwrench[extras]'"
    raise NotImplementedError(msg)


def dump(*args, **kwargs):
    msg = f"Cannot call function '{get_current_fn_name()}' because optional dependency 'pyyaml' is not installed. Please install it using 'pip install torchwrench[extras]'"
    raise NotImplementedError(msg)
