#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from argparse import ArgumentParser, Namespace
from dataclasses import asdict, dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Iterable, List, Literal, Optional, Tuple, Union
from unittest import TestCase

from pythonwrench.argparse import (
    get_parse_fn,
    parse_args_using_dataclass,
    parse_to_bool,
    parse_to_none,
    parse_to_optional_bool,
    parse_to_optional_float,
    parse_to_optional_int,
    parse_to_optional_str,
    parse_to_type,
)
from pythonwrench.typing import NoneType


class State(Enum):
    RUNNING = auto()
    PENDING = auto()
    SLEEPING = auto()


class TestArgparse(TestCase):
    def test_scalars_examples(self) -> None:
        assert parse_to_optional_str("None") is None
        assert parse_to_optional_str("null") is None

        assert parse_to_optional_bool("T")
        assert parse_to_optional_bool("false") is False
        assert parse_to_optional_bool("none") is None

        assert parse_to_bool("f") is False
        with self.assertRaises(ValueError):
            assert parse_to_bool("none")

        assert parse_to_optional_int("1") == 1
        assert parse_to_optional_int("10") == 10
        with self.assertRaises(ValueError):
            assert parse_to_optional_int("1.")

        assert parse_to_optional_float("1") == 1.0
        assert parse_to_optional_float("1.5") == 1.5

        assert parse_to_none("None") is None
        with self.assertRaises(ValueError):
            assert parse_to_none("")

    def test_parser(self) -> None:
        parser = ArgumentParser()
        target_type = Optional[Union[bool, int]]
        parse_fn = get_parse_fn(target_type)
        parser.add_argument("--val", type=parse_fn)

        args = parser.parse_args(["--val", "2"])
        assert isinstance(args.val, int)
        assert args.val == 2

        args = parser.parse_args(["--val", "f"])
        assert isinstance(args.val, bool)
        assert args.val is False

        args = parser.parse_args(["--val", "null"])
        assert isinstance(args.val, NoneType)
        assert args.val is None

        with self.assertRaises(SystemExit):
            args = parser.parse_args(["--val", "2.5"])

    def test_path(self) -> None:
        path = "/a/b.txt"
        assert get_parse_fn(Path)(path) == Path(path)

    def test_literal(self) -> None:
        type_ = Literal["winter", "summer", "fall", "spring"]
        assert get_parse_fn(type_)("summer") == "summer"

        with self.assertRaises(ValueError):
            assert get_parse_fn(type_)("something else") == "summer"

    def test_enum(self) -> None:
        assert parse_to_type("SLEEPING", State) == State.SLEEPING
        assert parse_to_type("pending", State) == State.PENDING

        with self.assertRaises(ValueError):
            assert parse_to_type("pending", State, case_sensitive=True) == State.PENDING

        with self.assertRaises(ValueError):
            assert parse_to_type("PENDING2", State) == State.PENDING


class TestDataclassParser(TestCase):
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
            arg3: List[float] = field(default_factory=list)
            arg4: Optional[str] = None
            arg5: List[Literal["linux", "windows", "mac"]] = field(default_factory=list)
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

    def test_parse_args_using_dataclass_example_3a(self) -> None:
        @dataclass
        class A:
            arg_a: List[List[int]] = field(default_factory=list)

        with self.assertRaises(TypeError):
            _ = parse_args_using_dataclass(A, args=[])

    def test_parse_args_using_dataclass_example_3b(self) -> None:
        @dataclass
        class B:
            arg_b: Union[str, List[str]] = ""

        with self.assertRaises(SystemExit):
            _ = parse_args_using_dataclass(B, args=[])

    def test_parse_args_using_dataclass_example_3c(self) -> None:
        @dataclass
        class C:
            arg_c: Tuple[str, ...] = ()

        with self.assertRaises(TypeError):
            _ = parse_args_using_dataclass(C, args=[])

    def test_parse_args_using_dataclass_example_3d(self) -> None:
        @dataclass
        class D:
            arg_d: int = 0

        with self.assertRaises(SystemExit):
            _ = parse_args_using_dataclass(D, args=["--arg_d", "1.1"])

    def test_parse_args_using_dataclass_example_4(self) -> None:
        @dataclass
        class A:
            nums: List[int] = field(default_factory=list)

        target = A(nums=[1, -1, 10])

        nums_args = list(map(str, target.nums))
        result = parse_args_using_dataclass(
            A, args=["--nums"] + nums_args, list_parsing="argparse"
        )
        assert target == result

        nums_args = [f"[{','.join(map(str, target.nums))}]"]
        result = parse_args_using_dataclass(
            A, args=["--nums"] + nums_args, list_parsing="brackets"
        )
        assert target == result

    def test_parse_args_using_dataclass_example_5(self) -> None:
        @dataclass
        class A:
            seed: int

        @dataclass
        class B(A):
            constraint_names: Optional[Iterable[str]] = ("b",)

        result = parse_args_using_dataclass(
            B,
            args=["--seed", "42"],
            list_parsing="brackets",
        )
        assert result == B(42, ("b",))

        result = parse_args_using_dataclass(
            B,
            args=["--constraint_names", "[a,b]", "--seed", "42"],
            list_parsing="brackets",
        )
        assert result == B(42, ["a", "b"]), f"{result=}"

        result = parse_args_using_dataclass(
            B,
            args=["--constraint_names", "[a]", "--seed", "42"],
            list_parsing="brackets",
        )
        assert result == B(42, ["a"])

        result = parse_args_using_dataclass(
            B,
            args=["--constraint_names", "[]", "--seed", "42"],
            list_parsing="brackets",
        )
        assert result == B(42, [])

        result = parse_args_using_dataclass(
            B,
            args=["--constraint_names", "none", "--seed", "42"],
            list_parsing="brackets",
        )
        assert result == B(42, None)

        with self.assertRaises(SystemExit):
            result = parse_args_using_dataclass(
                B,
                args=["--constraint_names", "truc", "--seed", "42"],
                list_parsing="brackets",
            )
            assert result == B(42, "truc")

    def test_parse_args_using_dataclass_example_6(self) -> None:
        @dataclass
        class A:
            seed: Optional[Iterable[Literal[0, "a"]]] = None

        result = parse_args_using_dataclass(
            A,
            args=[],
            list_parsing="brackets",
        )
        assert result == A()

        result = parse_args_using_dataclass(
            A,
            args=["--seed", "[0,a]"],
            list_parsing="brackets",
        )
        assert result == A([0, "a"])

        with self.assertRaises(SystemExit):
            result = parse_args_using_dataclass(
                A,
                args=["--seed", "[b]"],
                list_parsing="brackets",
            )
            assert result == A(["b"])  # type: ignore

        with self.assertRaises(SystemExit):
            result = parse_args_using_dataclass(
                A,
                args=["--seed", "[1]"],
                list_parsing="brackets",
            )
            assert result == A([1])  # type: ignore

    def test_parse_args_using_dataclass_example_7(self) -> None:
        @dataclass
        class Cfg1:
            path: Union[str, Path]

        @dataclass
        class Cfg2:
            a: int = 0
            b: str = ""

        expected_cfg1 = Cfg1(Path("test/a.txt"))
        expected_cfg2 = Cfg2(b="b")

        cfg = parse_args_using_dataclass(Cfg1, args=["--path", str(expected_cfg1.path)])
        assert cfg == expected_cfg1

        cfg2, cfg1 = parse_args_using_dataclass(
            Cfg2,
            Cfg1,
            args=[
                "--path",
                str(expected_cfg1.path),
                "--b",
                expected_cfg2.b,
            ],
        )
        assert cfg1 == expected_cfg1
        assert cfg2 == expected_cfg2

        args = parse_args_using_dataclass(
            Cfg2,
            Cfg1,
            args=[
                "--path",
                str(expected_cfg1.path),
                "--b",
                expected_cfg2.b,
            ],
            return_single_namespace=True,
        )
        expected_args = Namespace(**asdict(expected_cfg1), **asdict(expected_cfg2))
        assert args == expected_args

    def test_parse_store_bool(self) -> None:
        @dataclass
        class Cfg:
            test: bool = False
            num: int = 0
            create: bool = False

        target = Cfg(False, 10, True)
        cfg = parse_args_using_dataclass(
            Cfg,
            args=["--create", "--num", str(target.num)],
            bool_action="store_true",
        )
        assert cfg == target


if __name__ == "__main__":
    unittest.main()
