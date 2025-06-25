#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from pathlib import Path
from unittest import TestCase

from pythonwrench.cast import as_builtin, register_as_builtin_fn


class CustomClass:
    a: int = 0
    b: str = ""


class TestCast(TestCase):
    def test_example_1(self) -> None:
        examples = [
            ("a", "a"),
            ((), []),
            # note: on windows, forward slashes will be converted to backward slashes
            (Path("path/to/something"), str(Path("path/to/something"))),
            (["c", ("d",), {1, ()}], ["c", ["d"], [1, []]]),
            (CustomClass(), {"a": 0, "b": "", "added_prop": None}),
        ]

        @register_as_builtin_fn(CustomClass)
        def customclass_to_builtin(x: CustomClass) -> dict:
            return {"a": x.a, "b": x.b, "added_prop": None}

        for x, expected in examples:
            result = as_builtin(x)
            assert result == expected


if __name__ == "__main__":
    unittest.main()
