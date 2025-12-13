#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import (
    Any,
    ClassVar,
    Dict,
    Iterator,
    List,
    Protocol,
    Tuple,
    Union,
    runtime_checkable,
)

from typing_extensions import TypeAlias, TypeVar

NoneType: TypeAlias = type(None)  # type: ignore
EllipsisType: TypeAlias = type(...)  # type: ignore

BuiltinCollection: TypeAlias = Union[list, tuple, dict, set, frozenset]
BuiltinNumber: TypeAlias = Union[bool, int, float, complex]
BuiltinScalar: TypeAlias = Union[bool, int, float, complex, NoneType, str, bytes]

_T_Item = TypeVar("_T_Item", covariant=True)
_T_Index = TypeVar("_T_Index", contravariant=True, default=Any)
_T_Other = TypeVar("_T_Other", contravariant=True, default=Any)
_T_Index2 = TypeVar("_T_Index2", contravariant=True)

T_BuiltinNumber = TypeVar(
    "T_BuiltinNumber",
    bound=BuiltinNumber,
    default=BuiltinNumber,
    covariant=True,
)
T_BuiltinScalar = TypeVar(
    "T_BuiltinScalar",
    bound=BuiltinScalar,
    default=BuiltinScalar,
    covariant=True,
)

ListOrTuple = Union[List[_T_Item], Tuple[_T_Item, ...]]


@runtime_checkable
class DataclassInstance(Protocol):
    # Class meant for typing purpose only
    __dataclass_fields__: ClassVar[Dict[str, Any]]


@runtime_checkable
class NamedTupleInstance(Protocol):
    # Class meant for typing purpose only
    _fields: Tuple[str, ...]
    _field_defaults: Dict[str, Any]

    def _asdict(self) -> Dict[str, Any]:
        raise NotImplementedError

    def __getitem__(self, idx, /):
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError


@runtime_checkable
class SupportsAdd(Protocol[_T_Other]):
    def __add__(self, other: _T_Other, /):
        raise NotImplementedError


@runtime_checkable
class SupportsAnd(Protocol[_T_Other]):
    def __and__(self, other: _T_Other, /):
        raise NotImplementedError


@runtime_checkable
class SupportsBool(Protocol):
    def __bool__(self) -> bool:
        raise NotImplementedError


@runtime_checkable
class SupportsDiv(Protocol[_T_Other]):
    def __div__(self, other: _T_Other, /):
        raise NotImplementedError


@runtime_checkable
class SupportsGetitem(Protocol[_T_Item, _T_Index]):
    def __getitem__(self, idx: _T_Index, /) -> _T_Item:
        raise NotImplementedError


@runtime_checkable
class SupportsGetitem2(Protocol[_T_Index2, _T_Item]):
    """Same than `SupportsGetitem` except that generic parameters are in reversed order: [T_Index, T_Item]."""

    def __getitem__(self, idx: _T_Index2, /) -> _T_Item:
        raise NotImplementedError


@runtime_checkable
class SupportsGetitemLen(Protocol[_T_Item, _T_Index]):
    def __getitem__(self, idx: _T_Index, /) -> _T_Item:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError


@runtime_checkable
class SupportsGetitemLen2(Protocol[_T_Index2, _T_Item]):
    """Same than `SupportsGetitemLen` except that generic parameters are in reversed order: [T_Index, T_Item]."""

    def __getitem__(self, idx: _T_Index2, /) -> _T_Item:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError


@runtime_checkable
class SupportsGetitemIterLen(Protocol[_T_Item, _T_Index]):
    def __getitem__(self, idx: _T_Index, /) -> _T_Item:
        raise NotImplementedError

    def __iter__(self) -> Iterator[_T_Item]:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError


@runtime_checkable
class SupportsGetitemIterLen2(Protocol[_T_Index2, _T_Item]):
    """Same than `SupportsGetitemIterLen` except that generic parameters are in reversed order: [T_Index, T_Item]."""

    def __getitem__(self, idx: _T_Index2, /) -> _T_Item:
        raise NotImplementedError

    def __iter__(self) -> Iterator[_T_Item]:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError


@runtime_checkable
class SupportsIterLen(Protocol[_T_Item]):
    def __iter__(self) -> Iterator[_T_Item]:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError


@runtime_checkable
class SupportsLen(Protocol):
    def __len__(self) -> int:
        raise NotImplementedError


@runtime_checkable
class SupportsMul(Protocol[_T_Other]):
    def __mul__(self, other: _T_Other, /):
        raise NotImplementedError


@runtime_checkable
class SupportsOr(Protocol[_T_Other]):
    def __or__(self, other: _T_Other, /):
        raise NotImplementedError


@runtime_checkable
class SupportsMatmul(Protocol[_T_Other]):
    def __matmul__(self, other: _T_Other, /):
        raise NotImplementedError
