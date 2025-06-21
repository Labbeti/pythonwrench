#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .collections import (
    contained,
    dict_list_to_list_dict,
    dump_dict,
    filter_iterable,
    find,
    flat_dict_of_dict,
    flat_list_of_list,
    flatten,
    intersect_lists,
    list_dict_to_dict_list,
    recursive_generator,
    shuffled,
    sorted_dict,
    unflat_dict_of_dict,
    unflat_list_of_list,
    union_dicts,
    union_lists,
    unzip,
)
from .prop import (
    all_eq,
    all_ne,
    is_full,
    is_sorted,
    is_unique,
)
from .reducers import (
    intersect,
    prod,
    reduce_add,
    reduce_and,
    reduce_mul,
    reduce_or,
    sum,
    union,
)
