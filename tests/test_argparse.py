#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from argparse import ArgumentParser
from typing import Optional, Union
from unittest import TestCase

from pythonwrench.argparse import (
    parse_to,
    str_to_bool,
    str_to_none,
    str_to_optional_bool,
    str_to_optional_float,
    str_to_optional_int,
    str_to_optional_str,
)
from pythonwrench.typing import NoneType


class TestArgparse(TestCase):
    def test_scalars_examples(self) -> None:
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

        assert str_to_none("None") is None
        with self.assertRaises(ValueError):
            assert str_to_none("")

    def test_parser(self) -> None:
        parser = ArgumentParser()
        parser.add_argument("--val", type=parse_to(Optional[Union[bool, int]]))

        args = parser.parse_args(["--val", "2"])
        assert isinstance(args.val, int)
        assert args.val == 2

        args = parser.parse_args(["--val", "f"])
        assert isinstance(args.val, bool)
        assert not args.val

        args = parser.parse_args(["--val", "null"])
        assert isinstance(args.val, NoneType)
        assert args.val is None

        with self.assertRaises(SystemExit):
            args = parser.parse_args(["--val", "2.5"])


if __name__ == "__main__":
    unittest.main()
