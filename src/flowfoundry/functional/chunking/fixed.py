from __future__ import annotations
from typing import List, Dict, Any, Union
from copy import deepcopy

from ...strategies.registry import register_strategy

Chunk = Dict[str, Any]
InDoc = Dict[str, Any]


def _fixed_split(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """Deterministic fixed-size splitting into strings."""
    step = max(1, chunk_size - chunk_overlap)
    parts: List[str] = []
    for i in range(0, len(text), step):
        t = text[i : i + chunk_size]
        if t:
            parts.append(t)
    return parts


def _chunk_one_doc(
    doc: InDoc, chunk_size: int, chunk_overlap: int, default_doc_id: str
) -> List[Chunk]:
    """Split a single input dict with fixed-size logic, preserving metadata."""
    if "text" not in doc or not isinstance(doc["text"], str):
        raise ValueError(
            f"Expected doc['text'] to be a string, got {type(doc.get('text')).__name__}"
        )

    text = doc["text"]
    parts = _fixed_split(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    chunks: List[Chunk] = []
    offset = 0
    for i, p in enumerate(parts):
        idx = text.find(p, offset)
        if idx == -1:
            idx = offset
        out = deepcopy(doc)  # preserve all original metadata
        out["text"] = p
        out["start"] = idx
        out["end"] = idx + len(p)
        out.setdefault("doc", doc.get("doc", default_doc_id))
        out["chunk_index"] = i
        chunks.append(out)
        offset = idx + len(p)
    return chunks


@register_strategy("chunking", "fixed")
def fixed(
    data: Union[str, List[InDoc]],
    *,
    chunk_size: int = 800,
    chunk_overlap: int = 80,
    doc_id: str = "doc",
) -> List[Chunk]:
    """
    Fixed-size chunking that accepts:
      - a single string, or
      - a list of dicts with at least {'text': <str>} plus any extra metadata.

    Returns list[dict] where:
      - 'text' is the chunk text
      - 'start'/'end' are offsets within the original 'text'
      - all original metadata keys are preserved
      - 'doc' is preserved or set to `doc_id` if missing
      - 'chunk_index' is the chunk order within its parent doc
    """
    # Case 1: single string input
    if isinstance(data, str):
        text = data
        parts = _fixed_split(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks: List[Chunk] = []
        offset = 0
        for i, p in enumerate(parts):
            idx = text.find(p, offset)
            if idx == -1:
                idx = offset
            chunks.append(
                {
                    "doc": doc_id,
                    "text": p,
                    "start": idx,
                    "end": idx + len(p),
                    "chunk_index": i,
                }
            )
            offset = idx + len(p)
        return chunks

    # Case 2: list of dicts input
    if not isinstance(data, list):
        raise ValueError(
            f"Expected data to be str or list[dict], got {type(data).__name__}"
        )

    out: List[Chunk] = []
    for doc in data:
        if not isinstance(doc, dict):
            raise ValueError(f"Each item must be a dict, got {type(doc).__name__}")
        out.extend(
            _chunk_one_doc(
                doc,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                default_doc_id=doc_id,
            )
        )
    return out
