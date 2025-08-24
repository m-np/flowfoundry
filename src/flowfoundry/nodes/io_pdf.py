from __future__ import annotations
from typing import Dict, Any
from pathlib import Path
import pypdf
from ..registry import register_node


@register_node("io.pdf_load")
class PdfLoadNode:
    def __init__(self, path: str):
        self.path = path

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        reader = pypdf.PdfReader(Path(self.path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        state.setdefault("document", text)
        state.setdefault("doc_id", Path(self.path).stem)
        return state
