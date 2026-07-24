#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from argparse import ArgumentParser
from dataclasses import dataclass, field
from typing import List, Literal, Optional, Tuple, Union
from unittest import TestCase

from pythonwrench.argparse import (
    parse_args_using_dataclass,
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

    def test_parse_args_using_dataclass_example_1(self) -> None:
        @dataclass
        class A:
            a: int
            b: str = "b"
            c: float = 1.2

        target = A(a=0, c=0.5)
        args = ["--a", str(target.a), "--c", str(target.c)]
        output = parse_args_using_dataclass(A, args=args)
        assert output == target

    def test_parse_args_using_dataclass_example_2(self) -> None:
        @dataclass
        class A:
            arg1: None
            arg2: Literal["winter", "summer", "fall", "spring"]
            arg3: list[float] = field(default_factory=list)
            arg4: Optional[str] = None
            arg5: list[Literal["linux", "windows", "mac"]] = field(default_factory=list)
            arg6: Union[int, str] = 0

        target = A(arg1=None, arg2="fall", arg3=[99, 2])
        args = [
            "--arg1",
            str(target.arg1),
            "--arg2",
            target.arg2,
            "--arg3",
            "99",
            "2",
            "--arg5",
        ]
        output = parse_args_using_dataclass(A, args=args)

        assert output == target

    def test_parse_args_using_dataclass_example_3(self) -> None:
        @dataclass
        class A:
            arg_a: List[List[int]] = field(default_factory=list)

        with self.assertRaises(TypeError):
            _ = parse_args_using_dataclass(A, args=[])

        @dataclass
        class B:
            arg_b: Union[str, List[str]] = ""

        with self.assertRaises(TypeError):
            _ = parse_args_using_dataclass(B, args=[])

        @dataclass
        class C:
            arg_c: Tuple[str, ...] = ()

        with self.assertRaises(TypeError):
            _ = parse_args_using_dataclass(C, args=[])

        @dataclass
        class D:
            arg_d: int = 0

        with self.assertRaises(SystemExit):
            _ = parse_args_using_dataclass(D, args=["--arg_d", "1.1"])


if __name__ == "__main__":
    unittest.main()
