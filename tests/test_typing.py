#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from dataclasses import dataclass
from numbers import Number
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Literal,
    Mapping,
    NamedTuple,
    Optional,
    Tuple,
    TypedDict,
    Union,
)
from unittest import TestCase

from typing_extensions import NotRequired

from pythonwrench.typing import (
    NoneType,
    is_dataclass_instance,
    is_iterable_str,
    is_namedtuple_instance,
    is_typed_dict,
    isinstance_generic,
)


class ExampleDict(TypedDict):
    a: int
    b: str


class ExampleDict2(TypedDict):
    a: int
    b: str
    c: NotRequired[float]


class TestTypeChecks(TestCase):
    def test_is_iterable_str_1(self) -> None:
        inputs = [
            ("a", True, False),
            (["a"], True, True),
            ([], True, True),
            (("a",), True, True),
            ((), True, True),
            (1.0, False, False),
            ([["a"]], False, False),
            ("", True, False),
            ((s for s in ("a", "b", "c")), True, True),
        ]

        for x, expected_1, expected_2 in inputs:
            result_1 = is_iterable_str(x, accept_str=True)
            result_2 = is_iterable_str(x, accept_str=False)

            assert expected_1 == result_1
            assert expected_2 == result_2

    def test_is_dataclass_example_1(self) -> None:
        @dataclass
        class DC:
            a: int = 0
            b: str = "0"

        dc = DC(a=0, b="0")

        assert not is_namedtuple_instance(DC)
        assert not is_namedtuple_instance(dc)

        assert not is_dataclass_instance(DC)
        assert is_dataclass_instance(dc)

    def test_is_namedtuple_example_1(self) -> None:
        class NT1(NamedTuple):
            a: int
            b: str

        NT2 = NamedTuple("NT2", [("a", int), ("b", str)])

        nt1 = NT1(a=0, b="0")
        nt2 = NT2(a=0, b="0")

        assert not is_namedtuple_instance(NT1)
        assert not is_namedtuple_instance(NT2)
        assert is_namedtuple_instance(nt1)
        assert is_namedtuple_instance(nt2)

        assert not is_dataclass_instance(NT1)
        assert not is_dataclass_instance(NT2)
        assert not is_dataclass_instance(nt1)
        assert not is_dataclass_instance(nt2)


class TestIsInstanceGuard(TestCase):
    def test_example_1_int(self) -> None:
        x = 1

        assert isinstance_generic(x, int)
        assert isinstance_generic(x, Number)
        assert isinstance_generic(x, Optional[int])  # type: ignore
        assert isinstance_generic(x, Union[int, str])  # type: ignore
        assert isinstance_generic(x, Literal[1])  # type: ignore
        assert isinstance_generic(x, Literal[2, None, 1, "a"])  # type: ignore

        assert not isinstance_generic(x, float)
        assert not isinstance_generic(x, Callable)  # type: ignore
        assert not isinstance_generic(x, Generator)
        assert not isinstance_generic(x, Literal[2])  # type: ignore

    def test_example_2_dict(self) -> None:
        x = {"a": 2, "b": 10}

        assert isinstance_generic(x, dict)
        assert isinstance_generic(x, Dict)
        assert isinstance_generic(x, Mapping)

        assert isinstance_generic(x, Dict[str, int])
        assert isinstance_generic(x, Dict[Any, int])
        assert isinstance_generic(x, Dict[str, Any])
        assert isinstance_generic(x, Iterable[str])
        assert isinstance_generic(x, Mapping[str, int])
        assert isinstance_generic(x, Dict[Literal["b", "a"], Literal[10, 2]])

        assert not isinstance_generic(x, set)
        assert not isinstance_generic(x, Dict[str, float])
        assert not isinstance_generic(x, Dict[Literal["a"], Literal[10, 2]])

    def test_example_3_typed_dict(self) -> None:
        assert not is_typed_dict(dict)
        assert not is_typed_dict(Dict)
        assert not is_typed_dict(Dict[str, Any])
        assert is_typed_dict(ExampleDict)
        assert is_typed_dict(ExampleDict2)

        x = {"a": 1, "b": "dnqzudh"}

        assert isinstance_generic(x, Dict[str, Any])
        assert not isinstance_generic(x, Dict[str, int])
        assert isinstance_generic(x, Dict[str, Union[int, str]])
        assert isinstance_generic(x, Dict[Union[str, int], Union[int, str]])
        assert isinstance_generic(x, ExampleDict)
        assert isinstance_generic(x, ExampleDict2)

        x = {"a": 1, "b": 2}

        assert isinstance_generic(x, Dict[str, Any])
        assert isinstance_generic(x, Dict[str, int])
        assert isinstance_generic(x, Dict[str, Union[int, str]])
        assert isinstance_generic(x, Dict[Union[str, int], Union[int, str]])
        assert not isinstance_generic(x, ExampleDict)
        assert not isinstance_generic(x, ExampleDict2)

        x = {"a": 1, "b": "dnqzudh", "c": 2}

        assert isinstance_generic(x, Dict[str, Any])
        assert not isinstance_generic(x, Dict[str, int])
        assert isinstance_generic(x, Dict[str, Union[int, str]])
        assert isinstance_generic(x, Dict[Union[str, int], Union[int, str]])
        assert not isinstance_generic(x, ExampleDict)
        assert not isinstance_generic(x, ExampleDict2)

        x = {"a": []}

        assert isinstance_generic(x, Dict[str, Any])
        assert not isinstance_generic(x, Dict[str, int])
        assert not isinstance_generic(x, Dict[str, Union[int, str]])
        assert not isinstance_generic(x, Dict[Union[str, int], Union[int, str]])
        assert not isinstance_generic(x, ExampleDict)
        assert not isinstance_generic(x, ExampleDict2)

        x = {1: 1, "b": "dnqzudh"}

        assert not isinstance_generic(x, Dict[str, Any])
        assert not isinstance_generic(x, Dict[str, int])
        assert not isinstance_generic(x, Dict[str, Union[int, str]])
        assert isinstance_generic(x, Dict[Union[str, int], Union[int, str]])
        assert not isinstance_generic(x, ExampleDict)
        assert not isinstance_generic(x, ExampleDict2)

        x = {"a": 1, "b": "dnqzudh", "c": 3.0}

        assert isinstance_generic(x, Dict[str, Any])
        assert not isinstance_generic(x, Dict[str, int])
        assert not isinstance_generic(x, Dict[str, Union[int, str]])
        assert not isinstance_generic(x, Dict[Union[str, int], Union[int, str]])
        assert not isinstance_generic(x, ExampleDict)
        assert isinstance_generic(x, ExampleDict2)

    def test_tuple(self) -> None:
        examples = [
            ((), Tuple[()], True),
            ((1,), Tuple[()], False),
            ((1, 2), Tuple[()], False),
            ((), Tuple[int], False),
            ((1,), Tuple[int], True),
            ((1, 2), Tuple[int], False),
            ((), Tuple[int, ...], True),
            ((1,), Tuple[int, ...], True),
            ((1, 2), Tuple[int, ...], True),
            (("a", 2), Tuple[str, int], True),
            (("a", 2), Tuple[int, str], False),
            (("a", 2), Tuple[Union[str, int], ...], True),
            (("a", 2), Tuple[str, ...], False),
            (("a", 2), Tuple[int, ...], False),
            (("a", 2), Tuple[()], False),
            ([], Tuple[()], False),
            (("a",), Tuple[()], False),
        ]
        for example, type_, expected in examples:
            assert isinstance_generic(example, type_) == expected, (
                f"{example=}, {type_}"
            )

    def test_none(self) -> None:
        examples = [
            (1, int, True),
            (1, None, False),
            (1, NoneType, False),
            (1, Optional[int], True),
            (1, Union[int, None], True),
            (1, Union[int, NoneType], True),
            (1, Union[int, Optional[str]], True),
            (None, int, False),
            (None, None, True),
            (None, NoneType, True),
            (None, Optional[int], True),
            (None, Union[int, None], True),
            (None, Union[int, NoneType], True),
            (None, Union[int, Optional[str]], True),
            (2.5, Optional[int], False),
            ("", Optional[int], False),
        ]
        for example, type_, expected in examples:
            assert isinstance_generic(example, type_) == expected, (
                f"{example=}, {type_}"
            )

    def test_tuple_of_types(self) -> None:
        assert not isinstance_generic(1, ())
        assert isinstance_generic(1, (int,))
        assert isinstance_generic(1, (str, int))
        assert not isinstance_generic(1, (str,))

        assert not isinstance_generic("a", ())
        assert not isinstance_generic("a", (int,))
        assert isinstance_generic("a", (str, int))
        assert isinstance_generic("a", (str,))

        assert isinstance_generic(["a", "b"], (List[str], Tuple[str, ...]))
        assert isinstance_generic(("a", "b", "c"), (List[str], Tuple[str, ...]))
        assert isinstance_generic((), (List[str], Tuple[str, ...]))
        assert not isinstance_generic(("a",), (str,))

    def test_edges_cases(self) -> None:
        assert not isinstance_generic(1, Generator)
        assert isinstance_generic((i for i in range(5)), Generator)

        with self.assertRaises(TypeError):
            assert not isinstance_generic(
                (i for i in range(5)), Generator[int, None, None]
            )

        with self.assertRaises(TypeError):
            assert not isinstance_generic(1, Generator[int, None, None])


if __name__ == "__main__":
    unittest.main()
