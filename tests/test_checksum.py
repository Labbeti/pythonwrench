#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import random
import unittest
from unittest import TestCase

from pythonwrench.checksum import checksum_any
from pythonwrench.collections import all_ne
from pythonwrench.math import nextafter


class TestChecksum(TestCase):
    def test_checksum_alldiff(self) -> None:
        x = [
            list(range(10)),
            tuple(range(10)),
            set(range(10)),
            frozenset(range(10)),
            range(10),
            dict.fromkeys(range(10)),
            [],
            (),
            {},
            None,
            0,
            1,
            math.nan,
            [1, 2],
            [2, 1],
            [1, 2, 0],
            (1, 2),
            "abc",
            "",
            b"abc",
            b"",
            checksum_any,
            bytearray(),
        ]
        csums = [checksum_any(xi) for xi in x]
        assert all_ne(csums), f"{csums=}"

    def test_smallest_diff(self) -> None:
        x0 = random.random()
        x1 = nextafter(x0, 1.0)
        assert x0 != x1
        assert checksum_any(x0) != checksum_any(x1)

        x1 = nextafter(x0, -1.0)
        assert x0 != x1
        assert checksum_any(x0) != checksum_any(x1)

    def test_sets(self) -> None:
        s1 = {1, 2}
        s2 = {2, 1}
        assert s1 == s2
        assert checksum_any(s1) == checksum_any(s2)

    def test_enums(self) -> None:
        from enum import Enum

        class Color(Enum):
            RED = 1
            GREEN = 2
            BLUE = 3
            ROUGE = RED

        c1 = Color.RED
        c2 = Color.GREEN
        assert c1 != c2
        assert checksum_any(c1) != checksum_any(c2)

        assert Color.RED == Color.ROUGE
        assert checksum_any(Color.RED) == checksum_any(Color.ROUGE)


if __name__ == "__main__":
    unittest.main()
