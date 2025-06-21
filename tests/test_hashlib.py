#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import TestCase

from pythonwrench.hashlib import hash_file


class TestHashlib(TestCase):
    def test_disk_cache_example_1(self) -> None:
        tgt_fpath = Path(tempfile.gettempdir()).joinpath("tmp_test.py")
        shutil.copy(__file__, tgt_fpath)

        hash_value_1 = hash_file(__file__)
        hash_value_2 = hash_file(tgt_fpath)

        assert hash_value_1 == hash_value_2

        os.remove(tgt_fpath)


if __name__ == "__main__":
    unittest.main()
