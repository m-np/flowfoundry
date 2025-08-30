from __future__ import annotations
from typing import List, Union
from copy import deepcopy

from ...utils import InDoc, Chunk, register_strategy
from .recursive import recursive


@register_strategy("chunking", "hybrid")
def hybrid(
    data: Union[str, List[InDoc]],
    *,
    chunk_size: int = 800,
    chunk_overlap: int = 80,
    doc_id: str = "doc",
) -> List[Chunk]:
    """
    Hybrid chunking:
      1) Run recursive chunker to get fine-grained chunks.
      2) Merge small adjacent chunks (from the same 'doc') into larger ones:
         - If the current buffer's text length < chunk_size // 3, append the next chunk.
         - Otherwise, flush the buffer.

    Input:
      - data: str OR list of dicts with at least {"text": <str>} plus any metadata.

    Output:
      - list of dicts preserving original metadata; with 'text', 'start', 'end', and 'chunk_index'.
    """
    # Step 1: get base chunks via recursive
    parts: List[Chunk] = recursive(
        data, chunk_size=chunk_size, chunk_overlap=chunk_overlap, doc_id=doc_id
    )

    merged: List[Chunk] = []
    buf: Chunk | None = None

    for c in parts:
        # Defensive copies so we don't mutate upstream
        c = deepcopy(c)

        # Start a new buffer if empty
        if buf is None:
            buf = c
            continue

        # Merge only if same document id to avoid cross-doc merges
        same_doc = buf.get("doc") == c.get("doc")

        # If current buffer is "small", append next chunk's text; else flush
        if same_doc and len(str(buf.get("text", ""))) < (chunk_size // 3):
            # concatenate text with a newline separator
            buf_text = str(buf.get("text", ""))
            c_text = str(c.get("text", ""))
            new_text = (buf_text + "\n" + c_text) if buf_text else c_text

            # Update buffer text and end offset
            buf["text"] = new_text
            # 'start' remains the original buf['start']; 'end' should move forward
            if "end" in c:
                buf["end"] = c["end"]
            else:
                buf["end"] = buf.get("start", 0) + len(new_text)

            # You could optionally track merged children indices here if useful:
            # buf.setdefault("merged_from", []).extend([buf.get("chunk_index"), c.get("chunk_index")])
        else:
            # Flush buffer, start new one
            merged.append(buf)
            buf = c

    if buf is not None:
        merged.append(buf)

    # Re-number chunk_index to reflect post-merge ordering
    for i, m in enumerate(merged):
        m["chunk_index"] = i

        # Ensure start/end exist (for safety if upstream didn't set them)
        t = str(m.get("text", ""))
        if "start" not in m or not isinstance(m["start"], int):
            m["start"] = 0
        if "end" not in m or not isinstance(m["end"], int):
            m["end"] = m["start"] + len(t)

        # Ensure doc id is present
        m.setdefault("doc", doc_id)

    return merged
