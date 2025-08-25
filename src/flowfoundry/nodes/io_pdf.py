from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import importlib.resources as pkg_resources

from ..registry import register_node


def _repo_root(start: Optional[Path] = None) -> Optional[Path]:
    """Find the repo root by walking up until pyproject.toml is found."""
    cur = (start or Path.cwd()).resolve()
    for p in [cur, *cur.parents]:
        if (p / "pyproject.toml").exists():
            return p
    return None


def _is_glob(s: str) -> bool:
    return any(ch in s for ch in "*?[")


def _candidate_bases() -> List[Path]:
    bases: List[Path] = [Path.cwd()]
    rr = _repo_root()
    if rr:
        bases.append(rr)
    import os

    dd_env = os.environ.get("FLOWFOUNDRY_DATA_DIR")
    if dd_env:
        bases.append(Path(dd_env).expanduser())
    return bases


def _resolve_inputs(
    inputs: Union[str, Sequence[str]] | None,
    *,
    recursive: bool,
    patterns: Optional[Sequence[str]],
) -> List[Path]:
    """
    Expand inputs (abs/rel, dirs, globs) to concrete file paths.
    Searches current dir, repo root, and $FLOWFOUNDRY_DATA_DIR for relatives.
    Supports 'pkg:<filename>' for packaged assets.
    """
    if not inputs:
        return []
    if isinstance(inputs, str):
        inputs = [inputs]

    files: List[Path] = []
    bases = _candidate_bases()
    pats: Tuple[str, ...] = tuple(patterns or ("*.pdf", "*.txt", "*.md"))

    for raw in inputs:
        if raw.startswith("pkg:"):
            # packaged asset under flowfoundry/assets/
            name = raw.split("pkg:", 1)[1]
            try:
                pkg = pkg_resources.files("flowfoundry.assets")
                pkg_path = Path(str(pkg))  # convert Traversable -> filesystem path
                path = pkg_path / name
                if path.exists():
                    files.append(path)
                else:
                    # allow subfolders/globs under assets
                    files.extend(sorted(pkg_path.glob(name)))
            except Exception:
                pass
            continue

        p = Path(raw).expanduser()

        # Absolute path or explicit relative with glob?
        if p.is_absolute():
            if p.is_dir():
                for pat in pats:
                    files.extend(sorted(p.rglob(pat) if recursive else p.glob(pat)))
            else:
                if _is_glob(raw):
                    files.extend(sorted(Path("/").glob(raw.lstrip("/"))))
                elif p.exists():
                    files.append(p)
            continue

        # Relative paths: try each base
        if _is_glob(raw):
            for base in bases:
                files.extend(sorted(base.glob(raw)))
                if recursive:
                    files.extend(sorted(base.rglob(raw)))
        else:
            for base in bases:
                cand = (base / raw).resolve()
                if cand.is_dir():
                    for pat in pats:
                        files.extend(
                            sorted(cand.rglob(pat) if recursive else cand.glob(pat))
                        )
                elif cand.exists():
                    files.append(cand)

    # Deduplicate while preserving order
    seen: set[str] = set()
    uniq: List[Path] = []
    for f in files:
        s = f.as_posix()
        if s not in seen:
            uniq.append(f)
            seen.add(s)
    return uniq


def _read_text_from_file(path: Path, *, encoding: str = "utf-8") -> str:
    # Try PDF first (import lazily to avoid hard dependency)
    if path.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader as _PdfReader
        except Exception:
            _PdfReader = None

        if _PdfReader is not None:
            try:
                reader = _PdfReader(str(path))
                return "\n".join((page.extract_text() or "") for page in reader.pages)
            except Exception:
                # fall through to generic text fallback
                pass

    # Generic text fallback
    try:
        return path.read_text(encoding=encoding, errors="ignore")
    except Exception:
        try:
            return path.read_bytes().decode(encoding, errors="ignore")
        except Exception:
            return ""


def _fallback_sample() -> Tuple[str, Dict[str, Any]]:
    # packaged sample for resilient demos
    try:
        pkg = pkg_resources.files("flowfoundry.assets")
        pkg_path = Path(str(pkg))
        sample = pkg_path / "sample.pdf"
        text = _read_text_from_file(sample)
        return text or "FlowFoundry Sample Document", {
            "doc": "pkg:sample",
            "path": str(sample),
        }
    except Exception:
        return "FlowFoundry Sample Document", {"doc": "pkg:sample"}


@register_node("io.pdf_load")
class PdfLoadNode:
    """
    Load one or more documents into state["documents"] as a list of:
      { "doc_id": str, "text": str, "path": str, "metadata": {...} }

    Params:
    - path: str                       # single path, dir, or glob
    - paths: list[str] | str          # multiple paths/globs/dirs
    - recursive: bool = True          # recurse into directories
    - patterns: list[str]             # file patterns for directories (default: pdf/txt/md)
    - encoding: str = "utf-8"
    """

    def __init__(
        self,
        path: Optional[str] = None,
        paths: Optional[Union[str, Sequence[str]]] = None,
        recursive: bool = True,
        patterns: Optional[Sequence[str]] = None,
        encoding: str = "utf-8",
    ) -> None:
        self._inputs = paths if paths is not None else path
        self._recursive = recursive
        self._patterns = list(patterns) if patterns else None
        self._encoding = encoding

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        files = _resolve_inputs(
            self._inputs, recursive=self._recursive, patterns=self._patterns
        )
        documents: List[Dict[str, Any]] = []

        if not files:
            text, meta = _fallback_sample()
            documents.append(
                {
                    "doc_id": "pkg:sample",
                    "text": text,
                    "path": meta.get("path", "pkg:sample"),
                    "metadata": {"doc": "pkg:sample"},
                }
            )
        else:
            for p in files:
                text = _read_text_from_file(p, encoding=self._encoding)
                if not text.strip():
                    continue
                # Stable-ish doc_id: filename + short hash of full path
                short = hex(abs(hash(p.as_posix())) & 0xFFFF)[2:]
                doc_id = f"{p.stem}-{short}"
                documents.append(
                    {
                        "doc_id": doc_id,
                        "text": text,
                        "path": p.as_posix(),
                        "metadata": {"doc": p.name},
                    }
                )

        state["documents"] = documents
        # Back-compat: also expose first doc as "document"
        if documents and "document" not in state:
            state["document"] = documents[0]["text"]
            state["doc_id"] = documents[0]["doc_id"]
        return state
