#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import unittest
from unittest import TestCase

from pythonwrench.logging import (
    VERBOSE_WARNING,
    _verbose_to_logging_level,
    get_current_file_logger,
    get_ipython_name,
    get_null_logger,
    setup_logging_verbose,
)


class TestOS(TestCase):
    def test_example_1(self) -> None:
        assert get_ipython_name() is None
        assert get_current_file_logger() == logging.getLogger(__name__)

        logger = get_null_logger()
        setup_logging_verbose(logger, verbose=VERBOSE_WARNING)
        assert logger.level == _verbose_to_logging_level(VERBOSE_WARNING)


if __name__ == "__main__":
    unittest.main()
