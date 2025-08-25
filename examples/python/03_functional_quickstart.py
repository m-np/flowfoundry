"""
Functional API quickstart (no nodes):
- chunk text
- upsert/query Chroma
- (optionally) bm25 preselect
- craft a naive prompt and echo an answer
"""

from __future__ import annotations
import json
from typing import List, Dict
from flowfoundry.functional import (
    chunk_recursive,
    index_chroma_upsert,
    index_chroma_query,
    preselect_bm25,
)

DOC = """FlowFoundry: a strategy-first, cloud-agnostic agentic workflow framework.
It supports chunking, indexing, retrieval, reranking, prompting, and LLM chat."""


def main() -> None:
    # 1) Chunk
    chunks = chunk_recursive(DOC, size=60, overlap=10, doc_id="demo")
    print(f"Chunks: {len(chunks)}")

    # 2) Index (Chroma)
    coll = index_chroma_upsert(chunks, path=".ff_chroma_func", collection="docs_func")
    print(f"Collection: {coll}")

    # 3) Retrieve
    hits: List[Dict] = index_chroma_query(
        "What is FlowFoundry?", path=".ff_chroma_func", collection="docs_func", k=8
    )

    # 4) Rerank (BM25 preselect if available, else no-op)
    hits = preselect_bm25("What is FlowFoundry?", hits, top_k=5)

    # 5) Build prompt + echo
    context = "\n\n".join(h["text"] for h in hits)
    prompt = f"Using the context below, answer the question.\n\nContext:\n{context}\n\nQ: What is FlowFoundry?\nA:"
    answer = f"[ECHO] {prompt[:200]}..."
    print(json.dumps({"hits": len(hits), "answer": answer}, indent=2))


if __name__ == "__main__":
    main()
