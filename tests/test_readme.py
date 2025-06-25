#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest
from typing import Dict
from unittest import TestCase

import pythonwrench as pw


class TestReadmeExamples(TestCase):
    def test_collections_example_1(self) -> None:
        list_of_tuples = [(1, "a"), (2, "b"), (3, "c"), (4, "d")]
        assert pw.unzip(list_of_tuples) == ([1, 2, 3, 4], ["a", "b", "c", "d"])
        assert pw.flatten(list_of_tuples) == [1, "a", 2, "b", 3, "c", 4, "d"]

    def test_collections_example_2(self) -> None:
        values = [3, 1, 6, 4]
        assert pw.prod(values) == 72
        assert pw.argmax(values) == 2
        assert not pw.is_sorted(values)

    def test_collections_example_3(self) -> None:
        list_of_dicts = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        assert pw.list_dict_to_dict_list(list_of_dicts) == {"a": [1, 3], "b": [2, 4]}

    def test_collections_example_4(self) -> None:
        dict_of_dicts = {"a": {"x": 1, "y": 2}, "b": {"x": 3, "y": 4}}
        assert pw.flat_dict_of_dict(dict_of_dicts) == {
            "a.x": 1,
            "a.y": 2,
            "b.x": 3,
            "b.y": 4,
        }

    def test_typing_example_1(self) -> None:
        # Behaves like builtin isinstance() :
        assert pw.isinstance_generic({"a": 1, "b": 2}, dict)
        # But works with generic types !
        assert pw.isinstance_generic({"a": 1, "b": 2}, Dict[str, int])
        assert not pw.isinstance_generic({"a": 1, "b": 2}, Dict[str, str])

    def test_typing_example_2(self) -> None:
        # Combines Iterable and Sized !
        assert isinstance({"a": 1, "b": 2}, pw.SupportsGetitemLen)
        assert isinstance({"a": 1, "b": 2}, pw.SupportsIterLen)

    def test_disk_cache_example_1(self) -> None:
        @pw.disk_cache_decorator
        def heavy_processing():
            # Lot of stuff here
            ...

        _data1 = (
            heavy_processing()
        )  # first call function is called and the result is stored on disk
        _data2 = heavy_processing()  # second call result is loaded from disk directly

    def test_version_example_1(self) -> None:
        version = pw.Version("1.12.2")
        assert version.to_tuple() == (1, 12, 2)

        version = pw.Version("0.5.1-beta+linux")
        assert version.to_tuple() == (0, 5, 1, "beta", "linux")

    def test_serialization_example_1(self) -> None:
        list_of_dicts = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        pw.dump_csv(list_of_dicts, "data.csv")
        pw.dump_json(list_of_dicts, "data.json")
        assert pw.load_json("data.json") == list_of_dicts

        os.remove("data.csv")
        os.remove("data.json")


if __name__ == "__main__":
    unittest.main()
