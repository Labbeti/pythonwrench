#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pythonwrench._core import _insert_in_dict


def test_insert_in_dict_orders_by_priority() -> None:
    original = {
        "high": ("value", 10),
        "low": ("value", 1),
    }

    result = _insert_in_dict(original, "middle", ("value", 5), 5, priority_key=1)

    assert list(result) == ["high", "middle", "low"]
    assert original == {
        "high": ("value", 10),
        "low": ("value", 1),
    }


def test_insert_in_dict_ignores_existing_key() -> None:
    original = {"existing": ("original", 1)}

    result = _insert_in_dict(
        original, "existing", ("replacement", 10), 10, priority_key=1
    )

    assert result is original
    assert result["existing"] == ("original", 1)
