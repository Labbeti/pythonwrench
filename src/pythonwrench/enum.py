#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum

from typing_extensions import Self


class StrEnum(str, Enum):
    """StrEnum is the same as Enum, but its members are also strings and can be used in most of the same places that a string can be used.

    Note: when used as keys of dicts, enums are considered different from strings keys.

    This class has the same objective than https://docs.python.org/3/library/enum.html#enum.StrEnum, which was introduced in Python 3.11.
    """

    @classmethod
    def from_str(
        cls,
        value: str,
        case_sensitive: bool = False,
    ) -> Self:
        """Create an instance from str."""
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
        """Perform the generate next value operation."""
        return name

    @property
    def value(self) -> str:
        """Perform the value operation."""
        return self._value_

    def __eq__(self, other: object) -> bool:
        """Return whether this instance equals another object."""
        other = other.value if isinstance(other, Enum) else str(other)
        return self.value == other  # type: ignore

    def __hash__(self) -> int:
        """Return the hash of the instance."""
        return hash(self.value)

    def __str__(self) -> str:
        """Return the string representation of the instance."""
        return self.name
