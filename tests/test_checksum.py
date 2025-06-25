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
            range(10),
            [],
            (),
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


if __name__ == "__main__":
    unittest.main()
