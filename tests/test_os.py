#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest import TestCase

from pythonwrench.os import tree_iter


class TestOS(TestCase):
    def test_example_1(self) -> None:
        assert len(list(tree_iter(".."))) > 0


if __name__ == "__main__":
    unittest.main()
