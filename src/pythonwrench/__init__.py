#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Set of tools for Python that could be in the standard library."""

__name__ = "pythonwrench"
__author__ = "Étienne Labbé (Labbeti)"
__author_email__ = "labbeti.pub@gmail.com"
__license__ = "MIT"
__maintainer__ = "Étienne Labbé (Labbeti)"
__status__ = "Development"
__version__ = "0.2.0"


# Re-import for language servers
from . import abc as abc
from . import argparse as argparse
from . import collections as collections
from . import csv as csv
from . import dataclasses as dataclasses
from . import datetime as datetime
from . import difflib as difflib
from . import entries as entries
from . import enum as enum
from . import functools as functools
from . import hashlib as hashlib
from . import importlib as importlib
from . import inspect as inspect
from . import io as io
from . import json as json
from . import logging as logging
from . import math as math
from . import os as os
from . import pickle as pickle
from . import random as random
from . import re as re
from . import semver as semver
from . import warnings as warnings

# Global library imports
from .abc import Singleton
from .argparse import (
    str_to_bool,
    str_to_optional_bool,
    str_to_optional_float,
    str_to_optional_int,
    str_to_optional_str,
)
from .cast import as_builtin
from .checksum import checksum_any, register_checksum_fn
from .collections import (
    all_eq,
    all_ne,
    contained,
    dict_list_to_list_dict,
    dump_dict,
    filter_iterable,
    find,
    flat_dict_of_dict,
    flat_list_of_list,
    flatten,
    intersect,
    intersect_lists,
    is_full,
    is_sorted,
    is_unique,
    list_dict_to_dict_list,
    prod,
    recursive_generator,
    reduce_add,
    reduce_and,
    reduce_mul,
    reduce_or,
    shuffled,
    sorted_dict,
    sum,
    unflat_dict_of_dict,
    unflat_list_of_list,
    union,
    union_dicts,
    union_lists,
    unzip,
)
from .csv import dump_csv, load_csv
from .dataclasses import get_defaults_values
from .datetime import get_now, get_now_iso8601
from .difflib import find_closest_in_list, sequence_matcher_ratio
from .disk_cache import disk_cache_call, disk_cache_decorator
from .enum import StrEnum
from .functools import (
    Compose,
    compose,
    filter_and_call,
    function_alias,
    identity,
)
from .hashlib import hash_file
from .importlib import (
    is_available_package,
    is_editable_package,
    reload_editable_packages,
    reload_submodules,
    search_submodules,
)
from .inspect import get_argnames, get_current_fn_name, get_fullname
from .json import dump_json, load_json
from .logging import (
    VERBOSE_DEBUG,
    VERBOSE_ERROR,
    VERBOSE_INFO,
    VERBOSE_WARNING,
    MkdirFileHandler,
    get_current_file_logger,
    get_ipython_name,
    get_null_logger,
    log_once,
    running_on_interpreter,
    running_on_notebook,
    running_on_terminal,
    setup_logging_level,
    setup_logging_verbose,
)
from .math import argmax, argmin, argsort, clamp, clip
from .os import get_num_cpus_available, safe_rmdir, tree_iter
from .pickle import dump_pickle, load_pickle
from .random import randstr
from .re import (
    PatternLike,
    PatternListLike,
    compile_patterns,
    find_patterns,
    get_key_fn,
    match_patterns,
    sort_with_patterns,
)
from .semver import Version
from .typing import (
    BuiltinCollection,
    BuiltinNumber,
    BuiltinScalar,
    DataclassInstance,
    EllipsisType,
    NamedTupleInstance,
    NoneType,
    SupportsAdd,
    SupportsAnd,
    SupportsBool,
    SupportsGetitemIterLen,
    SupportsGetitemLen,
    SupportsIterLen,
    SupportsMul,
    SupportsOr,
    T_BuiltinNumber,
    T_BuiltinScalar,
    is_builtin_collection,
    is_builtin_number,
    is_builtin_obj,
    is_builtin_scalar,
    is_dataclass_instance,
    is_iterable_bool,
    is_iterable_bytes_or_list,
    is_iterable_float,
    is_iterable_int,
    is_iterable_integral,
    is_iterable_str,
    is_namedtuple_instance,
    is_sequence_str,
    is_typed_dict,
    isinstance_generic,
)
from .warnings import deprecated_alias, deprecated_function, warn_once

version = __version__
version_info = Version(__version__)
