#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import platform
import sys
import warnings
from pathlib import Path
from typing import Dict, Union

import pythonwrench
from pythonwrench.os import get_num_cpus_available
from pythonwrench.serialization.json import dumps_json

logger = logging.getLogger(__name__)


def main_info() -> None:
    """Show main packages versions."""
    warnings.filterwarnings("ignore", category=UserWarning)
    install_info = get_install_info()
    warnings.filterwarnings("default", category=UserWarning)
    dumped = dumps_json(install_info, to_builtins=True)
    print(dumped)


def get_install_info() -> Dict[str, Union[str, int]]:
    """Returns current installation information. Meant for debugging."""
    install_info = {
        "pythonwrench": pythonwrench.__version__,
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "os": platform.system(),
        "architecture": platform.architecture()[0],
        "num_cpus": get_num_cpus_available(),
        "package_path": get_package_repository_path(),
    }
    return install_info


def get_package_repository_path() -> str:
    """Return the absolute path where the source code of this package is installed."""
    return str(Path(__file__).parent.parent.parent)


if __name__ == "__main__":
    main_info()
