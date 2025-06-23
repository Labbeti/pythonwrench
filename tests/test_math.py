#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest import TestCase

from pythonwrench.collections import is_sorted
from pythonwrench.math import argmax, argmin, argsort


class TestMath(TestCase):
    def test_example_1(self) -> None:
        values = [3, 1, 2, 4, 6, 0, 5]

        assert argmax(values) == 4
        assert argmin(values) == 5

        indices = argsort(values)
        assert is_sorted([values[idx] for idx in indices])
        assert indices == [5, 1, 2, 0, 3, 6, 4]


if __name__ == "__main__":
    unittest.main()
