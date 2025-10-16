#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import unittest
from typing import Iterable, Literal, Mapping
from unittest import TestCase

from pythonwrench import inspect
from pythonwrench.inspect import get_argnames, get_current_fn_name, get_fullname


class DummyClass:
    def __init__(self, value: int = 0) -> None:
        attr = str(value)

        super().__init__()
        self.value = value
        self.attr = attr

    def f(self, x: int = 0) -> int:
        result = self.value + x
        return result


class TestInspect(TestCase):
    def test_example_1(self) -> None:
        x = [0, 1, 2]
        assert get_fullname(x) == "builtins.list(...)"

        x = 1.0
        assert get_fullname(x) == "builtins.float(...)"

        x = DummyClass()
        assert get_fullname(x) == f"{self.__module__}.DummyClass(...)"
        assert get_fullname(x.f) == f"{self.__module__}.DummyClass.f"

        assert get_fullname(DummyClass) == f"{self.__module__}.DummyClass"
        assert get_fullname(DummyClass.f) == f"{self.__module__}.DummyClass.f"

    def test_example_2(self) -> None:
        assert get_fullname(TestCase) == "unittest.case.TestCase"
        assert get_fullname(inspect) == "pythonwrench.inspect"
        assert get_fullname(get_fullname) == "pythonwrench.inspect.get_fullname"

        if sys.version_info.minor >= 11:
            assert get_fullname(Mapping) == "typing.Mapping"
            assert get_fullname(Iterable[str]) == "typing.Iterable[builtins.str]"
            assert (
                get_fullname(Iterable[Literal[1]])
                == "typing.Iterable[typing.Literal[builtins.int(...)]]"
            )

    def test_example_3(self) -> None:
        assert get_argnames(get_argnames) == ["fn"]
        assert get_argnames(DummyClass) == ["value"]
        assert get_argnames(DummyClass().f) == ["x"]

    def test_example_4(self) -> None:
        assert get_current_fn_name() == "test_example_4"

    def test_example_5(self) -> None:
        def f(x: int, y: str) -> str:
            return x * y

        assert get_argnames(f) == ["x", "y"]

    def test_example_6(self) -> None:
        class A:
            def __init__(self, a, /, b, c=2, *, d=3) -> None:
                super().__init__()
                self.a = a
                self.b = b
                self.c = c
                self.d = d

        assert get_argnames(A) == ["a", "b", "c", "d"]


if __name__ == "__main__":
    unittest.main()
