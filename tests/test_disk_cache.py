#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import unittest
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
            cache_fname_fmt="{fn_name}_{csum}.json",
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


if __name__ == "__main__":
    unittest.main()
