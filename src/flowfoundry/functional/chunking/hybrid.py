from __future__ import annotations
from typing import List, Dict
from ...strategies.registry import register_strategy
from .recursive import recursive

Chunk = Dict[str, object]


@register_strategy("chunking", "hybrid")
def hybrid(
    text: str, *, size: int = 800, overlap: int = 80, doc_id: str = "doc"
) -> List[Chunk]:
    parts = recursive(text, size=size, overlap=overlap, doc_id=doc_id)
    merged: List[Chunk] = []
    buf = None
    for c in parts:
        if buf is None:
            buf = c
        elif len(str(buf["text"])) < size // 3:
            buf["text"] = str(buf["text"]) + "\n" + str(c["text"])
            buf["end"] = c["end"]
        else:
            merged.append(buf)
            buf = c
    if buf is not None:
        merged.append(buf)
    return merged
