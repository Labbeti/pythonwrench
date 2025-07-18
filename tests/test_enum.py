#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from enum import auto
from unittest import TestCase

from pythonwrench.enum import StrEnum


class TestEnum(TestCase):
    def test_str_enum(self) -> None:
        class MyEnum(StrEnum):
            a = auto()
            b = auto()

        assert MyEnum.a == "a"
        assert MyEnum.b == "b"
        assert str(MyEnum.b) == "b"
        assert MyEnum.from_str("a") == MyEnum.a == "a"

        with self.assertRaises(ValueError):
            _ = MyEnum.from_str("c")

        assert {MyEnum.a: 1, "a": 2} == {MyEnum.a: 1, "a": 2}


if __name__ == "__main__":
    unittest.main()
