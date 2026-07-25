#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import platform
import sys
import warnings
from pathlib import Path
from typing import Any, Dict

import pythonwrench
from pythonwrench.os import get_num_cpus_available
from pythonwrench.serialization.json import dumps_json

logger = logging.getLogger(__name__)


def main_info() -> None:
    """Show main packages versions."""
    with warnings.catch_warnings():
        install_info = get_install_info()
    dumped = dumps_json(install_info, to_builtins=True)
    print(dumped)


def get_install_info() -> Dict[str, Any]:
    """Returns current installation information. Meant for debugging."""
    return {
        "os": platform.system(),
        "architecture": platform.architecture()[0],
        "num_cpus": get_num_cpus_available(),
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "pythonwrench": pythonwrench.__version__,
        "pythonwrench_path": get_pythonwrench_repository_path(),
    }


def get_pythonwrench_repository_path() -> str:
    """Return the absolute path where the source code of this package is installed."""
    return str(Path(__file__).parent.parent.parent)


if __name__ == "__main__":
    main_info()
