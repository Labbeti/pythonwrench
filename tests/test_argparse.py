#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest import TestCase

from pythonwrench.argparse import (
    str_to_bool,
    str_to_optional_bool,
    str_to_optional_float,
    str_to_optional_int,
    str_to_optional_str,
)


class TestArgparse(TestCase):
    def test_example_1(self) -> None:
        assert str_to_optional_str("None") is None
        assert str_to_optional_str("null") is None

        assert str_to_optional_bool("T")
        assert str_to_optional_bool("false") == False  # noqa: E712
        assert str_to_optional_bool("none") is None

        assert str_to_bool("f") == False  # noqa: E712
        with self.assertRaises(ValueError):
            assert str_to_bool("none")

        assert str_to_optional_int("1") == 1
        assert str_to_optional_int("10") == 10
        with self.assertRaises(ValueError):
            assert str_to_optional_int("1.")

        assert str_to_optional_float("1") == 1.0
        assert str_to_optional_float("1.5") == 1.5


if __name__ == "__main__":
    unittest.main()
