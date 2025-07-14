#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest import TestCase

from pythonwrench.jsonl import dumps_jsonl, loads_jsonl


class TestJSONL(TestCase):
    def test_example_1(self) -> None:
        data = [{"a": 1, "b": 2}, {"c": 3, "d": 4}]
        content = dumps_jsonl(data)
        assert loads_jsonl(content) == data


if __name__ == "__main__":
    unittest.main()
