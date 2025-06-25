#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from dataclasses import dataclass, field
from typing import List, Tuple
from unittest import TestCase

from pythonwrench.dataclasses import get_defaults_values, is_dataclass_instance


@dataclass
class Dummy:
    a: int
    b: str = "b"
    c: Tuple[int, ...] = ()
    d: List[str] = field(default_factory=list)


class TestDataclass(TestCase):
    def test_example_1(self) -> None:
        dummy = Dummy(2)
        assert is_dataclass_instance(dummy)
        assert get_defaults_values(dummy) == {"b": "b", "c": (), "d": []}


if __name__ == "__main__":
    unittest.main()
