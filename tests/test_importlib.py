#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import warnings
from unittest import TestCase

import pythonwrench as pw
from pythonwrench.importlib import (
    is_available_package,
    is_editable_package,
    reload_submodules,
    search_submodules,
)


class TestImportlib(TestCase):
    def test_example_1(self) -> None:
        reload_submodules(pw)

        assert is_available_package("pythonwrench")
        assert len(search_submodules(pw)) > 0

        assert not is_editable_package("typing_extensions")
        assert not is_editable_package("typing-extensions")

        assert is_available_package("pre_commit")
        assert is_available_package("typing_extensions")

        # ignore the UserWarning
        warnings.filterwarnings("ignore", category=UserWarning)
        assert is_available_package("pre-commit")
        assert is_available_package("typing-extensions")
        warnings.filterwarnings("default", category=UserWarning)


if __name__ == "__main__":
    unittest.main()
