#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import MISSING, dataclass, is_dataclass  # noqa: F401
from typing import Any, Dict, Type, TypeVar, cast

from typing_extensions import dataclass_transform

from pythonwrench.typing.checks import (  # noqa: F401
    is_dataclass_instance,
    is_dataclass_type,
)
from pythonwrench.typing.classes import Dataclass, DataclassInstance  # noqa: F401

T = TypeVar("T")


@dataclass_transform()
def dataclassdict(cls: Type[T]) -> Type[T]:
    """Decorate a class as a dataclass whose instances are also dictionaries.

    Dataclass fields can be read and assigned using either attribute or mapping
    syntax. Non-field dictionary keys are allowed, but do not become attributes.

    The decorator returns a subclass of *cls*, because Python cannot safely add
    ``dict`` to an existing class' bases.
    """
    dataclass_cls = dataclass(cls)
    conflicting_fields = sorted(
        set(dataclass_cls.__dataclass_fields__).intersection(dir(dict))  # type: ignore
    )
    if conflicting_fields:
        names = ", ".join(repr(name) for name in conflicting_fields)
        msg = f"Dataclass fields conflict with dict attributes: {names}."
        raise RuntimeError(msg)

    def setattr_(self: Any, name: str, value: Any) -> None:
        object.__setattr__(self, name, value)
        if name in self.__dataclass_fields__:
            dict.__setitem__(self, name, value)

    def setitem(self: Any, key: Any, value: Any) -> None:
        dict.__setitem__(self, key, value)
        if key in self.__dataclass_fields__:
            object.__setattr__(self, key, value)

    def delitem(self: Any, key: Any) -> None:
        dict.__delitem__(self, key)
        if key in self.__dataclass_fields__ and hasattr(self, key):
            object.__delattr__(self, key)

    def update(self: Any, *args: Any, **kwargs: Any) -> None:
        for key, value in dict(*args, **kwargs).items():
            setitem(self, key, value)

    def setdefault(self: Any, key: Any, default: Any = None) -> Any:
        if key not in self:
            setitem(self, key, default)
        return self[key]

    def pop(self: Any, key: Any, *default: Any) -> Any:
        if len(default) > 1:
            raise TypeError("pop expected at most 2 arguments")
        if key not in self:
            if default:
                return default[0]
            raise KeyError(key)
        value = self[key]
        delitem(self, key)
        return value

    def clear(self: Any) -> None:
        for key in list(self):
            delitem(self, key)

    namespace = {
        "__module__": cls.__module__,
        "__doc__": cls.__doc__,
        "__setattr__": setattr_,
        "__setitem__": setitem,
        "__delitem__": delitem,
        "update": update,
        "setdefault": setdefault,
        "pop": pop,
        "clear": clear,
    }
    result = type(cls.__name__, (dataclass_cls, dict), namespace)  # type: ignore
    result.__qualname__ = cls.__qualname__
    result = dataclass(result)
    return cast(Type[T], result)


def get_defaults_values(obj: DataclassInstance) -> Dict[str, Any]:
    defaults = {}

    for field in obj.__dataclass_fields__.values():
        if callable(field.default_factory):
            default = field.default_factory()
        else:
            default = field.default

        if default != MISSING:
            defaults[field.name] = default

    return defaults
