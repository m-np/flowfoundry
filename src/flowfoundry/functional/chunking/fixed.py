from __future__ import annotations
from typing import List, Dict
from ...strategies.registry import register_strategy

Chunk = Dict[str, object]


@register_strategy("chunking", "fixed")
def fixed(
    text: str, *, size: int = 800, overlap: int = 80, doc_id: str = "doc"
) -> List[Chunk]:
    chunks: List[Chunk] = []
    step = max(1, size - overlap)
    for i in range(0, len(text), step):
        t = text[i : i + size]
        if t:
            chunks.append({"doc": doc_id, "text": t, "start": i, "end": i + len(t)})
    return chunks
