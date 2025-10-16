#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importlib
import json
import logging
import sys
from functools import wraps
from importlib.metadata import Distribution, PackageNotFoundError
from importlib.util import find_spec
from types import ModuleType
from typing import Any, Callable, Dict, Iterable, List, Union

from typing_extensions import ParamSpec, TypeVar

from pythonwrench.warnings import warn_once

P = ParamSpec("P")
T = TypeVar("T")


_DEFAULT_SKIPPED = (
    "reimport_all",
    "get_ipython",
    "exit",
    "quit",
    "__name__",
    "__doc__",
    "__package__",
    "__loader__",
    "__spec__",
    "__builtin__",
    "__builtins__",
)

logger = logging.getLogger(__name__)


def is_available_package(package: str) -> bool:
    """Returns True if package is installed in the current python environment."""
    if "-" in package:
        msg = f"Found character '-' in package name '{package}'. (it will be replaced by '_')"
        warn_once(msg)
        package = package.replace("-", "_")

    try:
        return find_spec(package) is not None
    except AttributeError:
        # Old support for Python <= 3.6
        return False
    except (ImportError, ModuleNotFoundError):
        # Python >= 3.7
        return False


def is_editable_package(package: str) -> bool:
    """Returns True if package is installed in editable mode in the current python environment."""
    # TODO: check if this works with package containing - or _
    try:
        direct_url = Distribution.from_name(package).read_text("direct_url.json")
    except PackageNotFoundError:
        return False
    if direct_url is None:
        return False
    editable = json.loads(direct_url).get("dir_info", {}).get("editable", False)
    return editable


def search_submodules(
    root: ModuleType,
    only_editable: bool = True,
    only_loaded: bool = False,
) -> List[ModuleType]:
    """Return the submodules already imported."""

    def _impl(
        root: ModuleType,
        accumulator: Dict[ModuleType, None],
    ) -> Dict[ModuleType, None]:
        attrs = [getattr(root, attr_name) for attr_name in dir(root)]
        submodules = [
            attr
            for attr in attrs
            if isinstance(attr, ModuleType) and attr not in accumulator
        ]
        submodules = {
            submodule
            for submodule in submodules
            if (
                (
                    not only_editable
                    or is_editable_package(submodule.__name__.split(".")[0])
                )
                and (not only_loaded or submodule.__name__ in sys.modules)
            )
        }
        accumulator.update(dict.fromkeys(submodules))

        for submodule in submodules:
            accumulator = _impl(submodule, accumulator)
        return accumulator

    submodules = _impl(root, {root: None})
    submodules = list(submodules)
    submodules = submodules[::-1]
    return submodules


def reload_submodules(
    *modules: ModuleType,
    verbose: int = 0,
    only_editable: bool = True,
    only_loaded: bool = False,
) -> List[ModuleType]:
    """Reload all submodule recursively."""
    candidates: Dict[ModuleType, None] = {}
    for module in modules:
        submodules = search_submodules(
            module,
            only_editable=only_editable,
            only_loaded=only_loaded,
        )
        candidates.update(dict.fromkeys(submodules))

    for candidate in candidates:
        if verbose > 0:
            logger.info(f"Reload '{candidate}'...")
        try:
            importlib.reload(candidate)
        except ModuleNotFoundError as err:
            msg = f"ModuleNotFound: did this module '{candidate.__name__}' has been renamed after starting execution?"
            logger.warning(msg)
            raise err

    return list(candidates)


def reload_editable_packages(*, verbose: int = 0) -> List[ModuleType]:
    """Reload all submodules of editable packages already imported."""
    pkg_names = {name.split(".")[0] for name in sys.modules.keys()}
    editable_packages = [
        sys.modules[name] for name in pkg_names if is_editable_package(name)
    ]
    if verbose >= 2:
        msg = f"{len(editable_packages)}/{len(pkg_names)} editable packages found: {editable_packages}"
        logger.debug(msg)

    return reload_submodules(
        *editable_packages,
        verbose=verbose,
        only_editable=True,
        only_loaded=False,
    )


class Placeholder:
    """Placeholder object. All instances attributes always returns the object itself."""

    def __init__(self, *args, **kwargs) -> None: ...

    def __getattr__(self, name: str) -> Any:
        return self

    def __call__(self, *args, **kwargs) -> Any:
        return self

    def __getitem__(self, *args, **kwargs) -> Any:
        return self

    def __eq__(self, other) -> Any:
        return self == other

    def __ne__(self, other) -> Any:
        return self != other


def requires_packages(
    arg0: Union[Iterable[str], str],
    /,
    *args: str,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to wrap a function and raises an error if the function is called.

    Example
    -------
    >>> @requires_packages("pandas")
    >>> def f(x):
    >>>     return x
    >>> f(1)  # raises ImportError if pandas is not installed
    """
    if isinstance(arg0, str):
        packages = [arg0] + list(args)
    elif isinstance(arg0, Iterable):
        packages = list(arg0) + list(args)
    else:
        raise TypeError(f"Invalid arguments types {(arg0,) + args}.")

    def _wrap(fn: Callable[P, T]) -> Callable[P, T]:
        @wraps(fn)
        def _impl(*args: P.args, **kwargs: P.kwargs) -> T:
            missing = [pkg for pkg in packages if not is_available_package(pkg)]
            if len(missing) == 0:
                return fn(*args, **kwargs)
            else:
                prefix = "\n - "
                missing_str = prefix.join(missing)
                msg = (
                    f"Cannot use/import objects because the following optionals dependencies are missing:"
                    f"{prefix}{missing_str}\n"
                )
                raise ImportError(msg)

        return _impl

    return _wrap
