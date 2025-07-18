#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile
import unittest
from pathlib import Path
from unittest import TestCase

from pythonwrench.json import read_json, save_json


class TestJSON(TestCase):
    def test_example_1(self) -> None:
        tmp_fpath = Path(tempfile.gettempdir()).joinpath("test.json")
        data = {"x": [1, 2], "y": "abc", "z": None}
        save_json(data, tmp_fpath)
        result = read_json(tmp_fpath)
        assert data == result
        os.remove(tmp_fpath)


if __name__ == "__main__":
    unittest.main()
