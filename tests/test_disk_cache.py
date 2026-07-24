#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import unittest
from typing import Dict, List
from unittest import TestCase

import pythonwrench as pw


class TestDiskCache(TestCase):
    def test_disk_cache_example_1(self) -> None:
        def heavy_processing(x: float):
            return random.random() * x

        x = random.random()
        data1 = pw.disk_cache_call(heavy_processing, x)
        data2 = pw.disk_cache_call(heavy_processing, x)
        data3 = pw.disk_cache_call(heavy_processing, x * 2)

        assert data1 == data2
        assert data1 != data3

    def test_disk_cache_example_2(self) -> None:
        @pw.disk_cache_decorator(
            cache_fname_fmt="{fn_name}_{checksum}_x={x}.json",
            cache_load_fn=pw.load_json,
            cache_dump_fn=pw.dump_json,
        )
        def heavy_processing(x: float) -> float:
            return random.random() * x

        x = random.random()
        data1 = heavy_processing(x)
        data2 = heavy_processing(x)
        data3 = heavy_processing(x * 2)

        assert data1 == data2
        assert data1 != data3

    def test_disk_cache_example_3(self) -> None:
        cache_fname = "disk_cache_example_3.csv"

        @pw.disk_cache_decorator(
            cache_saving_backend="csv",
            cache_fname_fmt=cache_fname,
        )
        def disk_cache_example_3(num: int) -> List[Dict[str, str]]:
            return pw.dict_list_to_list_dict(
                {"a": ["a"] * num, "b": ["b"] * num}, "same"
            )

        outputs = disk_cache_example_3(10)

        assert disk_cache_example_3.fn(10) == outputs  # type: ignore
        assert (disk_cache_example_3.cache_fn_dpath / cache_fname).is_file()  # type: ignore


if __name__ == "__main__":
    unittest.main()
