#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import unittest
from unittest import TestCase

from pythonwrench.csv import dump_csv, load_csv


class TestCSV(TestCase):
    def test_csv(self) -> None:
        examples = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        expected_with_header = "a,b\r\n1,2\r\n3,4\r\n"
        assert dump_csv(examples) == expected_with_header

        expected_without_header = "1,2\r\n3,4\r\n"
        assert dump_csv(examples, header=False) == expected_without_header

        expected_from_dumped = [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}]
        assert load_csv(io.StringIO(expected_with_header)) == expected_from_dumped


if __name__ == "__main__":
    unittest.main()
