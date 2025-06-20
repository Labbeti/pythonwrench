#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum
from typing import Type, TypeVar

T_StrEnum = TypeVar("T_StrEnum", bound="StrEnum")


class StrEnum(str, Enum):
    """StrEnum is the same as Enum, but its members are also strings and can be used in most of the same places that a string can be used.

    This class has the same objective than https://docs.python.org/3/library/enum.html#enum.StrEnum, which was introduced in Python 3.11.
    """

    @classmethod
    def from_str(
        cls: Type[T_StrEnum],
        value: str,
        case_sensitive: bool = False,
    ) -> T_StrEnum:
        members = cls.__members__.keys()
        for member in members:
            if member == value or (
                not case_sensitive and member.lower() == value.lower()
            ):
                return cls[member]

        msg = f"Invalid argument {value=}. (expected one of {tuple(members)})"
        raise ValueError(msg)

    @staticmethod
    def _generate_next_value_(name, start, count, last_values) -> str:
        return name

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        other = other.value if isinstance(other, Enum) else str(other)
        return self.value == other  # type: ignore

    def __hash__(self) -> int:
        return hash(self.value)
