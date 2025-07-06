#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile
import unittest
from pathlib import Path
from unittest import TestCase

from pythonwrench.csv import dumps_csv, loads_csv, read_csv, save_csv


class TestCSV(TestCase):
    def test_examples_1(self) -> None:
        examples = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        expected_with_header = "a,b\r\n1,2\r\n3,4\r\n"
        assert dumps_csv(examples) == expected_with_header

        expected_without_header = "1,2\r\n3,4\r\n"
        assert dumps_csv(examples, header=False) == expected_without_header

        expected_from_dumped = [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}]
        assert loads_csv(expected_with_header) == expected_from_dumped

    def test_examples_2(self) -> None:
        examples = [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}]
        tmp_dpath = Path(tempfile.gettempdir())

        tmp_fpath = tmp_dpath.joinpath("subdir", "test.csv")
        save_csv(examples, tmp_fpath, overwrite=True, make_parents=True)
        result = read_csv(tmp_fpath, orient="list")

        assert examples == result
        os.remove(tmp_fpath)


if __name__ == "__main__":
    unittest.main()
