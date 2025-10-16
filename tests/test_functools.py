#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest import TestCase

from pythonwrench.functools import get_argnames


class TestFunctools(TestCase):
    def test_get_argnames_example_1(self) -> None:
        def f(x: int, y: str) -> str:
            return x * y

        assert get_argnames(f) == ["x", "y"]

    def test_get_argnames_example_2(self) -> None:
        class A:
            def __init__(self, x, /, y, *, z=2) -> None:
                super().__init__()

        assert get_argnames(A) == ["x", "y", "z"]


if __name__ == "__main__":
    unittest.main()
