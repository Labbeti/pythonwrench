#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest import TestCase

from pythonwrench.functools import filter_and_call, get_argnames


class TestFunctools(TestCase):
    def test_example_1(self) -> None:
        class A:
            def __init__(self, a, /, b, c=2, *, d=3) -> None:
                super().__init__()
                self.a = a
                self.b = b
                self.c = c
                self.d = d

        assert get_argnames(A) == ["a", "b", "c", "d"]
        assert filter_and_call(A, a=1, b=2, c=0).c == 0
        assert filter_and_call(A, a=1, b=2, non_existent=0).c == 2

    def test_example_2(self) -> None:
        def f(x, y):
            return x + y

        assert filter_and_call(f, y=2, x=1, z=0) == 3


if __name__ == "__main__":
    unittest.main()
