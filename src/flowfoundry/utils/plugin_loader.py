from __future__ import annotations
from pathlib import Path
from typing import Iterable, List, Tuple, Dict, Any
import importlib.util
import sys
import types


def _load_module_from_path(path: Path) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import module from: {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(path.stem, mod)
    spec.loader.exec_module(mod)
    return mod


def _export_functions_from_module(mod: types.ModuleType) -> List[Tuple[str, str, str]]:
    """
    If module defines:
      FF_EXPORTS = [(family, name, alias?), ...]
    bind those registry functions into `flowfoundry.functional` as attributes.
    """
    out: List[Tuple[str, str, str]] = []
    if not hasattr(mod, "FF_EXPORTS"):
        return out

    entries = getattr(mod, "FF_EXPORTS")
    if not isinstance(entries, (list, tuple)):
        return out

    from flowfoundry.utils.functional_registry import strategies
    import flowfoundry.functional as ff

    for entry in entries:
        if not isinstance(entry, (list, tuple)) or not (2 <= len(entry) <= 3):
            continue
        family: str = entry[0]
        name: str = entry[1]
        alias: str = entry[2] if len(entry) == 3 else name
        fn = strategies.get(family, name)  # raises if not registered yet
        setattr(ff, alias, fn)
        out.append((family, name, alias))
    return out


def load_plugins(
    paths: Iterable[str | Path],
    *,
    export_to_functional: bool = True,
    glob: str = "*.py",
) -> Dict[str, Any]:
    """
    Import files/dirs so their @register_strategy decorators run.
    Optionally export selected functions into flowfoundry.functional via FF_EXPORTS.

    Each path may be a file.py or a directory (recursively scanned by `glob`).
    Returns: {"imported": [...], "exported": [(family,name,alias), ...]}
    """
    imported: List[str] = []
    exported: List[Tuple[str, str, str]] = []

    for raw in paths:
        p = Path(raw).resolve()
        if not p.exists():
            continue
        files = [p] if p.is_file() else [q for q in p.rglob(glob) if q.is_file()]

        for file_path in files:
            mod = _load_module_from_path(file_path)
            imported.append(str(file_path))
            if export_to_functional:
                exported.extend(_export_functions_from_module(mod))

    return {"imported": imported, "exported": exported}
