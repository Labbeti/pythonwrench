#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from dataclasses import asdict, dataclass, field, is_dataclass
from typing import List, Tuple
from unittest import TestCase

from pythonwrench.dataclasses import (
    add_dict_methods,
    dataclassdict,
    get_defaults_values,
    is_dataclass_instance,
)


@dataclass
class Dummy:
    a: int
    b: str = "b"
    c: Tuple[int, ...] = ()
    d: List[str] = field(default_factory=list)


class TestDataclass(TestCase):
    def test_example_1(self) -> None:
        dummy = Dummy(2)

        assert is_dataclass(dummy)
        assert is_dataclass(Dummy)
        assert is_dataclass_instance(dummy)
        assert not is_dataclass_instance(Dummy)

        assert get_defaults_values(dummy) == {"b": "b", "c": (), "d": []}

    def test_dataclassdict(self) -> None:
        @dataclassdict
        class Point:
            x: int
            y: int = 0

        point = Point(1)
        assert is_dataclass(point)
        assert isinstance(point, dict)
        assert dict(point) == {"x": 1, "y": 0}
        assert len(point) == 2
        assert asdict(point) == {"x": 1, "y": 0}

        point.x = 2
        assert point["x"] == 2

        point["y"] = 3
        assert point.y == 3

        point.update(x=4, extra=True)
        assert point.x == 4
        assert point["extra"] is True

    def test_dataclassdict_rejects_dict_attribute_as_field(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "'keys'"):

            @dataclassdict
            class Invalid:
                keys: float = 0.0

    def test_add_dict_methods(self) -> None:
        @dataclass
        class Existing:
            a: int = 1
            b: str = ""

        ExistingDict = add_dict_methods(Existing)
        value = ExistingDict()

        assert isinstance(value, Existing)
        assert isinstance(value, dict)
        assert value["a"] == 1
        assert value["b"] == ""

    def test_add_dict_methods_rejects_non_dataclass(self) -> None:
        class Regular:
            pass

        with self.assertRaisesRegex(TypeError, "expects a dataclass type"):
            add_dict_methods(Regular)


if __name__ == "__main__":
    unittest.main()
