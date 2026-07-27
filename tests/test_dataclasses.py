#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from dataclasses import asdict, dataclass, field, is_dataclass
from typing import List, Tuple
from unittest import TestCase

from pythonwrench.dataclasses import (
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


if __name__ == "__main__":
    unittest.main()
