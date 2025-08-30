# src/flowfoundry/utils/functional_autodiscover.py
from __future__ import annotations

import importlib
import pkgutil
from types import ModuleType
from typing import Iterable, List

import flowfoundry.functional as functional_pkg


def _iter_submodules(pkg: ModuleType) -> Iterable[str]:
    """Yield full module names under a package (non-dunder)."""
    for m in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
        if any(part.startswith("_") for part in m.name.split(".")):
            continue
        yield m.name


def import_all_functional() -> List[str]:
    """
    Import every submodule under flowfoundry.functional.*
    to ensure @register_strategy has been executed.
    Returns list of imported module names.
    """
    imported: List[str] = []
    for mod_name in _iter_submodules(functional_pkg):
        importlib.import_module(mod_name)
        imported.append(mod_name)
    return imported
