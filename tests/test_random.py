#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest import TestCase

from pythonwrench.random import randstr


class TestOS(TestCase):
    def test_example_1(self) -> None:
        sizes = [
            (10,),
            (2, 5),
            (10, 20),
        ]

        for args in sizes:
            for _ in range(10):
                if len(args) == 1:
                    min_, max_ = args[0], args[0] + 1
                elif len(args) == 2:
                    min_, max_ = args
                else:
                    raise RuntimeError

                result = randstr(*args)
                assert min_ <= len(result) < max_


if __name__ == "__main__":
    unittest.main()
