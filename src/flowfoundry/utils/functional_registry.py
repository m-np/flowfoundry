from __future__ import annotations

import os
import sys
import logging
import importlib
import pkgutil
from dataclasses import dataclass, field
from typing import Callable, Dict, TypeVar, ParamSpec, cast, List, Tuple, Set
from importlib.metadata import entry_points
from typing import Any

# Pull the contract version (and custom errors if you later want to use them)
from .functional_contracts import STRATEGY_CONTRACT_VERSION

P = ParamSpec("P")
R = TypeVar("R")

_log = logging.getLogger(__name__)

# Track packages we've already scanned to keep imports idempotent
_LOADED_PACKAGES: Set[str] = set()

_PLUGIN_PACKAGE_NAMES = ("flowfoundry_plugin", "flowfoundry_plugins")


def _import_all_submodules(package_name: str) -> None:
    """
    Recursively import all submodules under `package_name` once.
    Importing executes any @register_strategy decorators in those modules.
    Safe to call repeatedly; imports are idempotent per package.
    """
    if package_name in _LOADED_PACKAGES:
        return

    try:
        pkg = importlib.import_module(package_name)
    except Exception as e:
        _log.debug("FF autodiscover: cannot import %s: %s", package_name, e)
        return

    # Single module (no __path__): importing it already ran decorators.
    if not hasattr(pkg, "__path__"):
        _LOADED_PACKAGES.add(package_name)
        return

    for _, modname, _ in pkgutil.walk_packages(pkg.__path__, prefix=pkg.__name__ + "."):
        try:
            importlib.import_module(modname)
        except Exception as e:
            _log.debug("FF autodiscover: failed importing %s: %s", modname, e)

    _LOADED_PACKAGES.add(package_name)


def _import_namespace_plugins(namespace: str) -> None:
    """
    PEP 420 namespace discovery:
    If the namespace package exists (and may span multiple distributions),
    import *all* submodules contributed under it so that their decorators run.
    """
    try:
        ns_pkg = importlib.import_module(namespace)
    except Exception:
        return  # namespace not present; nothing to do

    # Walk the namespace’s path list (can span multiple dists)
    for _, modname, _ in pkgutil.walk_packages(
        ns_pkg.__path__, prefix=ns_pkg.__name__ + "."
    ):
        try:
            importlib.import_module(modname)
        except Exception as e:
            _log.debug("FF namespace import failed for %s: %s", modname, e)


def _ensure_on_syspath(path: str) -> None:
    """Prepend a folder to sys.path if not already present."""
    if not path:
        return
    norm = os.path.abspath(path)
    if norm not in [os.path.abspath(p) for p in sys.path]:
        sys.path.insert(0, norm)


def _ascend_paths(start: str) -> List[str]:
    """Yield start, its parents up to filesystem root (inclusive)."""
    out: List[str] = []
    cur = os.path.abspath(start)
    while True:
        out.append(cur)
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return out


def _find_local_plugin_packages() -> List[Tuple[str, str]]:
    """
    Discover local plugin packages by scanning:
      - current working dir and its parents,
      - every existing sys.path entry,
    for directories named 'flowfoundry_plugin' or 'flowfoundry_plugins'.

    We also check common dev subfolders (e.g., 'src', 'source', 'python', 'py', 'lib')
    so repos without packaging still work:

        repo-root/
          src/flowfoundry_plugin/...
          # or
          src/flowfoundry_plugins/...

    Returns a list of (package_name, parent_dir) tuples, where parent_dir is what
    we add to sys.path so that 'import flowfoundry_plugin' succeeds.
    """
    found: Set[Tuple[str, str]] = set()

    # Common development subdirs to check under each root candidate
    SUBDIRS = ("", "src", "source", "python", "py", "lib")

    def _scan_root(root: str) -> None:
        for sub in SUBDIRS:
            base = os.path.join(root, sub) if sub else root
            if not os.path.isdir(base):
                continue
            for pkg_name in _PLUGIN_PACKAGE_NAMES:
                candidate = os.path.join(base, pkg_name)
                if os.path.isdir(candidate):
                    # parent_dir must be the directory we add to sys.path
                    found.add((pkg_name, base))

    # 1) cwd and all parents (covers running tests from subdirs)
    for root in _ascend_paths(os.getcwd()):
        _scan_root(root)

    # 2) existing sys.path entries (editable installs, dev shells, etc.)
    for base in list(sys.path):
        if isinstance(base, str) and base:
            _scan_root(os.path.abspath(base))

    return sorted(found)


@dataclass
class StrategyRegistries:
    """
    Heterogeneous registry: strategies may have different call signatures.

    Example structure:
        families = {
            "ingestion": {"name": callable, ...},
            "chunking":  {"name": callable, ...},
            "indexing":  {"name": callable, ...},
            "rerank":    {"name": callable, ...},
            "compose":   {"name": callable, ...},
        }
    """

    families: Dict[str, Dict[str, Callable[..., object]]] = field(default_factory=dict)

    def register(self, family: str, name: str, fn: Callable[..., object]) -> None:
        self.families.setdefault(family, {})[name] = fn

    def get(self, family: str, name: str) -> Callable[..., Any]:
        try:
            return self.families[family][name]
        except KeyError as e:
            avail = list(self.families.get(family, {}).keys())
            raise KeyError(
                f"Strategy '{family}:{name}' not found. Available: {avail}"
            ) from e

    def has(self, family: str, name: str) -> bool:
        return name in self.families.get(family, {})

    def list_families(self) -> List[str]:
        return list(self.families.keys())

    def list_names(self, family: str) -> List[str]:
        return list(self.families.get(family, {}).keys())

    def load_entrypoints(self) -> None:
        """
        Discover and register strategies exposed via:

          (1) flowfoundry.strategies.<family>   — explicit callable entry points
              (backward-compatible behavior)

          (2) flowfoundry.plugins               — package/module entry points
              Each entry point can point to a package or module; we import & scan
              all submodules so any @register_strategy decorators run.

          (3) PEP 420 namespaces:
              - 'flowfoundry_plugins' (plural)
              - 'flowfoundry_plugin'  (singular)
              Auto-discover and import all contributed modules.

          (4) Local, un-packaged folders named:
              - 'flowfoundry_plugins' or 'flowfoundry_plugin'
              found under the current working dir / parents or any sys.path entry.
              We temporarily ensure their parent is on sys.path and import recursively.
        """
        eps = entry_points()

        # (1) Existing explicit callables
        for family in ("ingestion", "chunking", "indexing", "rerank", "compose"):
            for ep in eps.select(group=f"flowfoundry.strategies.{family}"):
                self.register(family, ep.name, ep.load())

        # (2) Package-level plugins (zero-maintenance as new code is added)
        for ep in eps.select(group="flowfoundry.plugins"):
            try:
                obj = ep.load()
                modname = getattr(obj, "__name__", None)
                if isinstance(modname, str):
                    _import_all_submodules(modname)
                elif callable(obj):
                    # Allow custom discover() function if provided
                    obj()
            except Exception as e:
                _log.debug("FF plugin EP load failed for %s: %s", ep, e)

        # (3) Namespace-based discovery (no env vars, no per-repo code)
        for ns in _PLUGIN_PACKAGE_NAMES:
            _import_namespace_plugins(ns)

        # (4) Local raw folders (not packaged) under cwd/parents and sys.path
        for pkg_name, parent_dir in _find_local_plugin_packages():
            try:
                _ensure_on_syspath(parent_dir)
                _import_all_submodules(pkg_name)
            except Exception as e:
                _log.debug(
                    "FF local plugin import failed for %s at %s: %s",
                    pkg_name,
                    parent_dir,
                    e,
                )

    def autoload(
        self,
        packages: List[str] | None = None,
        *,
        env_var: str = "FF_STRATEGY_PACKAGES",
    ) -> None:
        """
        Import+scan packages so decorator-registered strategies are available
        without explicit entry points. If `packages` is None, read comma/space-
        separated names from the environment variable FF_STRATEGY_PACKAGES.
        """
        if packages is None:
            raw = os.getenv(env_var, "")
            tokens = [t.strip() for part in raw.split(",") for t in part.split()]
            packages = [t for t in tokens if t]
        for name in packages:
            _import_all_submodules(name)


# Global registry instance (backward compatible)
strategies = StrategyRegistries()


def register_strategy(
    family: str, name: str
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator that registers a strategy and preserves the callable's type.

    Usage:
        @register_strategy("chunking", "fixed")
        def fixed(...): ...
    """

    def deco(fn: Callable[P, R]) -> Callable[P, R]:
        strategies.register(family, name, cast(Callable[..., object], fn))
        return fn

    return deco


def strategy_contract_version() -> str:
    return STRATEGY_CONTRACT_VERSION


__all__ = [
    "StrategyRegistries",
    "strategies",
    "register_strategy",
    "strategy_contract_version",
]
