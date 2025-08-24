from __future__ import annotations
from typing import List, Dict, Optional, Any, cast
from ...strategies.registry import register_strategy
from .fixed import fixed

RecursiveCharacterTextSplitter: Optional[Any]
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter as _RCTS

    RecursiveCharacterTextSplitter = _RCTS
except Exception:
    RecursiveCharacterTextSplitter = None

Chunk = Dict[str, object]


@register_strategy("chunking", "recursive")
def recursive(
    text: str, *, size: int = 800, overlap: int = 80, doc_id: str = "doc"
) -> List[Chunk]:
    if RecursiveCharacterTextSplitter is None:
        return fixed(text, size=size, overlap=overlap, doc_id=doc_id)
    splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap)
    parts: List[str] = cast(List[str], splitter.split_text(text))
    chunks: List[Chunk] = []
    offset = 0
    for p in parts:
        idx = text.find(p, offset)
        if idx == -1:
            idx = offset
        chunks.append({"doc": doc_id, "text": p, "start": idx, "end": idx + len(p)})
        offset = idx + len(p)
    return chunks
