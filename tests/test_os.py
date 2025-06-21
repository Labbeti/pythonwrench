#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from pathlib import Path
from unittest import TestCase

from pythonwrench.os import get_num_cpus_available, safe_rmdir, tree_iter


class TestOS(TestCase):
    def test_example_1(self) -> None:
        assert len(list(tree_iter(".."))) > 0

    def test_example_2(self) -> None:
        Path("a/b/c").mkdir(parents=True, exist_ok=True)
        Path("a/b/d").mkdir(parents=False, exist_ok=True)
        safe_rmdir("a")

    def test_example_3(self) -> None:
        assert get_num_cpus_available() >= 0


if __name__ == "__main__":
    unittest.main()
