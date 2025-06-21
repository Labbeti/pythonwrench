#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import unittest
from unittest import TestCase

from pythonwrench.functools import disk_cache_call


class TestDiskCache(TestCase):
    def test_disk_cache_example_1(self) -> None:
        def heavy_processing(x: float):
            return random.random() * x

        x = random.random()
        data1 = disk_cache_call(heavy_processing, x)
        data2 = disk_cache_call(heavy_processing, x)
        data3 = disk_cache_call(heavy_processing, x * 2)

        assert data1 == data2
        assert data1 != data3


if __name__ == "__main__":
    unittest.main()
