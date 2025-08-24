from __future__ import annotations
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import os

import pypdf
from importlib import resources as importlib_resources

from ..registry import register_node


def _find_project_root(start: Path) -> Optional[Path]:
    """Walk up until we find a pyproject.toml; return its directory or None."""
    for p in (start,) + tuple(start.parents):
        if (p / "pyproject.toml").exists():
            return p
    return None


def _resolve_path(user_path: str) -> Tuple[Optional[Path], str]:
    """
    Try several resolution strategies. Return (path-or-None, how).
    how ∈ {"pkg","absolute","cwd","repo","env","notfound"}
    """
    if user_path.startswith("pkg:"):
        # Package asset: flowfoundry/assets/<rest>
        return None, "pkg"

    p = Path(user_path)

    # Absolute path
    if p.is_absolute():
        return (p if p.exists() else None), "absolute"

    # Relative to CWD
    cand = Path.cwd() / p
    if cand.exists():
        return cand, "cwd"

    # Relative to repo root (if present)
    root = _find_project_root(Path.cwd())
    if root:
        cand = root / p
        if cand.exists():
            return cand, "repo"

    # Relative to env dir
    env_dir = os.environ.get("FLOWFOUNDRY_DATA_DIR")
    if env_dir:
        cand = Path(env_dir) / p
        if cand.exists():
            return cand, "env"

    return None, "notfound"


def _read_pdf_file(path: Path) -> str:
    reader = pypdf.PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _read_pkg_pdf(rel_name: str) -> Optional[str]:
    """
    Read a PDF bundled in package assets (flowfoundry/assets/<rel_name>).
    Return text if found, else None.
    """
    try:
        res = importlib_resources.files("flowfoundry") / "assets" / rel_name
        if not res.is_file():
            return None
        with res.open("rb") as fh:
            reader = pypdf.PdfReader(fh)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        return None


def _fallback_text() -> str:
    return (
        "FlowFoundry Sample Document\n\n"
        "This is built-in sample text used when the requested PDF is not found.\n"
        "You can place your PDFs under:\n"
        "  - <current working directory>\n"
        "  - <your repo root>\n"
        "  - path from $FLOWFOUNDRY_DATA_DIR\n"
        "Or reference packaged assets via 'pkg:sample.pdf'.\n"
    )


@register_node("io.pdf_load")
class PdfLoadNode:
    def __init__(self, path: str):
        self.path = path

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # 1) Try pkg: assets first if requested
        if self.path.startswith("pkg:"):
            rel = self.path.split("pkg:", 1)[1].lstrip("/")
            text = _read_pkg_pdf(rel)
            if text is not None:
                state.setdefault("document", text)
                state.setdefault("doc_id", Path(rel).stem or "pkg_doc")
                return state
            # Fallthrough to regular resolution if asset missing

        # 2) Resolve a real filesystem path
        resolved, how = _resolve_path(self.path)

        if resolved is not None:
            # Happy path
            try:
                text = _read_pdf_file(resolved)
                state.setdefault("document", text)
                state.setdefault("doc_id", resolved.stem)
                return state
            except FileNotFoundError:
                pass  # will fall back below

        # 3) Provide a helpful message and fallback text (keeps the workflow running)
        tried = []
        p = Path(self.path)
        tried.append(f"CWD: {Path.cwd() / p}")
        root = _find_project_root(Path.cwd())
        if root:
            tried.append(f"REPO: {root / p}")
        env_dir = os.environ.get("FLOWFOUNDRY_DATA_DIR")
        if env_dir:
            tried.append(f"ENV ($FLOWFOUNDRY_DATA_DIR): {Path(env_dir) / p}")
        tried.append("PKG: pkg:sample.pdf (bundled asset)")

        print(  # noqa: T201 (intentional: user-facing hint)
            "io.pdf_load: file not found. Looked in:\n  - "
            + "\n  - ".join(str(t) for t in tried)
            + "\nUsing built-in sample text so the flow can continue."
        )

        state.setdefault("document", _fallback_text())
        # doc_id reflects user's intent even if file missing
        state.setdefault("doc_id", p.stem or "missing_doc")
        return state
