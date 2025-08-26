from __future__ import annotations
from typing import List, Optional, Any, cast, Union
from copy import deepcopy

from ...utils import InDoc, Chunk, register_strategy
from .fixed import fixed

RecursiveCharacterTextSplitter: Optional[Any]
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter as _RCTS

    RecursiveCharacterTextSplitter = _RCTS
except Exception:
    RecursiveCharacterTextSplitter = None


def _chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """Chunk a single string using RCTS if available, else fixed()."""
    if RecursiveCharacterTextSplitter is None:
        fixed_chunks = fixed(
            text, chunk_size=chunk_size, chunk_overlap=chunk_overlap, doc_id=""
        )
        return [cast(str, ch["text"]) for ch in fixed_chunks]
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return cast(List[str], splitter.split_text(text))


def _chunk_one_doc(
    doc: InDoc, chunk_size: int, chunk_overlap: int, default_doc_id: str
) -> List[Chunk]:
    """Chunk a single input dict, preserving metadata and adding start/end offsets."""
    if "text" not in doc or not isinstance(doc["text"], str):
        raise ValueError(
            f"Expected doc['text'] to be a string, got {type(doc.get('text')).__name__}"
        )

    text = doc["text"]
    parts = _chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    chunks: List[Chunk] = []
    offset = 0
    for i, p in enumerate(parts):
        idx = text.find(p, offset)
        if idx == -1:
            idx = offset
        out = deepcopy(doc)  # preserve all input metadata
        out["text"] = p  # replace with chunk text
        out["start"] = idx
        out["end"] = idx + len(p)
        out.setdefault("doc", doc.get("doc", default_doc_id))
        out["chunk_index"] = i
        chunks.append(out)
        offset = idx + len(p)
    return chunks


@register_strategy("chunking", "recursive")
def recursive(
    data: Union[str, List[InDoc]],
    *,
    chunk_size: int = 800,
    chunk_overlap: int = 80,
    doc_id: str = "doc",
) -> List[Chunk]:
    """
    Recursive chunking that accepts:
      - a single string, or
      - a list of dicts with at least {"text": <str>} plus any extra metadata.

    Returns a list of dicts where:
      - 'text' is the chunk text
      - 'start'/'end' are offsets within the original 'text'
      - all original metadata keys are preserved
      - 'doc' is preserved or set to `doc_id` if missing
      - 'chunk_index' indicates the chunk order within its parent doc
    """
    # Case 1: single string input
    if isinstance(data, str):
        text = data
        parts = _chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
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
