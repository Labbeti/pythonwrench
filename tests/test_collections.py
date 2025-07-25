#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import random
import unittest
from collections import Counter
from typing import List
from unittest import TestCase

from pythonwrench.collections import (
    all_eq,
    all_ne,
    contained,
    dict_list_to_list_dict,
    dump_dict,
    duplicate_list,
    find,
    flat_dict_of_dict,
    flat_list_of_list,
    flatten,
    intersect_lists,
    is_sorted,
    list_dict_to_dict_list,
    recursive_generator,
    reduce_add,
    shuffled,
    unflat_dict_of_dict,
    unflat_list_of_list,
    union_dicts,
    union_lists,
)
from pythonwrench.re import get_key_fn
from pythonwrench.typing import isinstance_generic


class TestAllEqAllNe(TestCase):
    def test_all_eq(self) -> None:
        x = [1, 2, 3, 4]
        assert not all_eq(x)

        x = [1] * 10
        assert all_eq(x)
        assert all_eq([random.randint(0, 2**20)])
        assert all_eq([])
        assert all_eq(())

    def test_all_ne(self) -> None:
        lst = [random.randint(0, 10) for _ in range(100)]

        assert all_ne(set(lst))
        assert all_ne([random.randint(0, 2**20)])
        assert all_ne([])
        assert all_ne(())


class TestDictListToListDict(TestCase):
    def test_example_1(self) -> None:
        x = {"a": [1, 2], "b": [3, 4]}
        expected = [{"a": 1, "b": 3}, {"a": 2, "b": 4}]
        result = dict_list_to_list_dict(x)

        assert result == expected

    def test_example_2(self) -> None:
        x = {"a": [1, 2, 3], "b": [4], "c": [5, 6]}
        expected = [
            {"a": 1, "b": 4, "c": 5},
            {"a": 2, "b": -1, "c": 6},
            {"a": 3, "b": -1, "c": -1},
        ]
        result = dict_list_to_list_dict(x, key_mode="union", default_val=-1)

        assert result == expected


class TestFlatDict(TestCase):
    def test_example_1(self) -> None:
        x = {
            "a": 1,
            "b": {
                "a": 2,
                "b": 10,
            },
        }
        expected = {"a": 1, "b.a": 2, "b.b": 10}

        output = flat_dict_of_dict(x)
        assert output == expected

    def test_example_2(self) -> None:
        x = {"a": ["hello", "world"], "b": 3}
        expected = {"a.0": "hello", "a.1": "world", "b": 3}

        output = flat_dict_of_dict(x, flat_iterables=True)
        assert output == expected

    def test_example_3(self) -> None:
        x = {"a": {"b": 1}, "a.b": 2}
        expected = {"a.b": 2}

        output = flat_dict_of_dict(x)
        assert output == expected

    def test_example_4(self) -> None:
        x = {"a": {"b": 1}, "a.b": 2}
        self.assertRaises(ValueError, flat_dict_of_dict, x, overwrite=False)

    def test_unflat_dict_example_1(self) -> None:
        x = {
            "a.a": 1,
            "b.a": 2,
            "b.b": 3,
            "c": 4,
        }
        y = {"a": {"a": 1}, "b": {"a": 2, "b": 3}, "c": 4}

        y_hat = unflat_dict_of_dict(x)
        assert y_hat == y


class TestListDictToDictList(TestCase):
    def test_example_1(self) -> None:
        lst = [{"a": 1, "b": 2}, {"a": 4, "b": 3, "c": 5}]
        output = list_dict_to_dict_list(
            lst,
            key_mode="union",
            default_val=0,
        )
        expected = {"a": [1, 4], "b": [2, 3], "c": [0, 5]}
        assert output == expected

    def test_example_2(self) -> None:
        lst = [{"a": 1, "b": 2}, {"a": 4, "b": 3, "c": 5}]

        with self.assertRaises(ValueError):
            list_dict_to_dict_list(
                lst,
                default_val=None,
                key_mode="same",
            )

    def test_example_3(self) -> None:
        lst = [{"a": 1, "b": 2, "c": 3}, {"a": 11, "b": 22, "c": 33}]
        output = list_dict_to_dict_list(
            lst,
            default_val=None,
            key_mode="same",
        )
        expected = {"a": [1, 11], "b": [2, 22], "c": [3, 33]}
        assert output == expected


class TestIntersectLists(TestCase):
    def test_example_1(self) -> None:
        input_ = [["a", "b", "b", "c"], ["c", "d", "b", "a"], ["b", "a", "a", "e"]]
        expected = ["a", "b"]
        output = intersect_lists(input_)
        assert output == expected


class TestFlatList(TestCase):
    def test_example_1(self) -> None:
        lst = [
            list(map(str, range(random.randint(0, 100))))
            for _ in range(random.randint(0, 10))
        ]
        for sublst in lst:
            random.shuffle(sublst)
        random.shuffle(lst)

        assert isinstance_generic(lst, List[List[str]])

        flatten, sizes = flat_list_of_list(lst)
        assert isinstance_generic(flatten, List[str])
        assert len(lst) == len(sizes)
        assert len(flatten) == sum(sizes)

        unflat = unflat_list_of_list(flatten, sizes)
        assert isinstance_generic(unflat, List[List[str]])
        assert len(lst) == len(unflat)
        assert lst == unflat

    def test_example_2(self) -> None:
        lst = ["a", "b", "c", "d", "e"]
        sizes = [1, 0, 2, 1, 3]
        result = duplicate_list(lst, sizes)
        expected = ["a", "c", "c", "d", "e", "e", "e"]
        assert result == expected


class TestGetKeyFn(TestCase):
    def test_example_1(self) -> None:
        lst = ["a", "abc", "aa", "abcd"]
        patterns = ["^ab.*"]  # sort list with elements starting with 'ab' first
        result = list(sorted(lst, key=get_key_fn(patterns)))
        expected = ["abc", "abcd", "a", "aa"]
        assert result == expected


class TestFlatten(TestCase):
    def test_example_1(self) -> None:
        xlst = [[[3.0, 0, 1], ["a", None, 2], range(3)]]
        expected = [3.0, 0, 1, "a", None, 2, 0, 1, 2]
        result = flatten(xlst)
        assert result == expected

    def test_example_2(self) -> None:
        xlst = [[range(0, 3), range(3, 6)], [range(6, 9), range(9, 12)]]

        expected = list(range(0, 12))
        result = flatten(xlst)
        assert result == expected

        expected = [list(range(0, 6)), list(range(6, 12))]
        result = flatten(xlst, 1, 2)
        assert result == expected

        expected = [range(0, 3), range(3, 6), range(6, 9), range(9, 12)]
        result = flatten(xlst, 0, 1)
        assert result == expected


class TestRecursiveGenerator(TestCase):
    def test_example_1(self) -> None:
        xlst = [[[3.0, 0, 1], ["a", None, 2], range(3)]]
        expected = list(zip([3.0, 0, 1, "a", None, 2, 0, 1, 2], [0, 1, 2] * 3, [3] * 9))
        result = list(recursive_generator(xlst))
        assert result == expected

    def test_example_2(self) -> None:
        xlst = [[range(0, 3), range(3, 6)], [range(6, 9), range(9, 12)]]

        expected = list(zip(range(0, 12), [0, 1, 2] * 4, [3] * 12))
        result = list(recursive_generator(xlst))
        assert result == expected


class TestIsSorted(TestCase):
    def test_example_1(self) -> None:
        x_sorted = list(range(10))
        x = copy.copy(x_sorted)
        x[0] = x_sorted[-1]
        x[-1] = x_sorted[0]

        tests = [
            (x_sorted, True),
            (x, False),
            ([], True),
            ([2], True),
            ([2, 2], True),
            ([2, 3], True),
        ]

        for input_, expected in tests:
            assert is_sorted(input_) == expected


class TestSearch(TestCase):
    def test_contained_example_1(self) -> None:
        assert contained(2, [1, 2, 3, 4])
        assert not contained(5, [1, 2, 3, 4])
        assert not contained(2, [1, 2, 3, 4], [2])

    def test_find_example_1(self) -> None:
        assert find("b", ["a", "b", "c", "d"]) == 1
        assert find("e", ["a", "b", "c", "d"]) == -1

        assert (
            find(
                "B",
                ["a", "b", "c", "d"],
                match_fn=lambda x, y: x.lower() == y,
                order="left",
            )
            == 1
        )


class TestDump(TestCase):
    def test_example(self) -> None:
        x = {"a": 1, "b": 2, "c": 3}
        assert dump_dict(x) == "a=1, b=2, c=3"


class TestShuffle(TestCase):
    def test_example_1(self) -> None:
        x = [random.randint(0, 10) for _ in range(100)]
        assert Counter(shuffled(x)) == Counter(x)


class TestReduce(TestCase):
    def test_union_dicts(self) -> None:
        dicts = [{"a": 1}, {"a": 2, "b": 3}, {"c": 4}, {"b": 5}]
        expected = {"a": 2, "b": 5, "c": 4}
        assert union_dicts(dicts) == expected

    def test_union_lists(self) -> None:
        lists = [[1, 3, 2], [3, 4, 1]]
        expected = [1, 3, 2, 4]
        assert union_lists(lists) == expected

    def test_reduce_add(self) -> None:
        args = [1, 2, 3]

        assert reduce_add(args) == 6
        assert reduce_add(args, start=-3) == 3

        assert reduce_add(*args) == 6
        assert reduce_add(*args, start=10) == 16

        assert reduce_add([], start=2) == 2
        assert reduce_add(start=4) == 4

        with self.assertRaises(ValueError):
            assert reduce_add([])

        with self.assertRaises(ValueError):
            assert reduce_add()  # type: ignore

        assert reduce_add(args, args) == [1, 2, 3, 1, 2, 3]
        assert reduce_add(args, args, start=[4]) == [4, 1, 2, 3, 1, 2, 3]

        with self.assertRaises(TypeError):
            assert reduce_add(args, args, start=1)


if __name__ == "__main__":
    unittest.main()
