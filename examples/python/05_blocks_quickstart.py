"""
Blocks API: compose strategy blocks directly in Python code (no nodes).
Requires Chroma installed for indexing/query steps.
"""

from __future__ import annotations
from typing import List, Dict
from flowfoundry.blocks import Recursive, ChromaUpsert, ChromaQuery, BM25
import json

DOC = """FlowFoundry makes agentic RAG simple. You can mix strategies like chunking,
indexing, retrieval, and reranking to build robust pipelines."""


def main() -> None:
    # 1) Chunk
    chunker = Recursive(size=80, overlap=10)
    chunks: List[Dict] = chunker(text=DOC, doc_id="blocks-demo")

    # 2) Index
    upsert = ChromaUpsert(path=".ff_chroma_blocks", collection="docs_blocks")
    coll_name: str = upsert(chunks=chunks)

    # 3) Query
    query = ChromaQuery(path=".ff_chroma_blocks", collection="docs_blocks", k=6)
    hits: List[Dict] = query(query="What is FlowFoundry?")

    # 4) Rerank (BM25 preselect; no-op if rank_bm25 not installed)
    bm25 = BM25(top_k=5)
    hits = bm25("What is FlowFoundry?", hits)

    # 5) Simple echo "answer"
    context = "\n".join(h["text"] for h in hits)
    prompt = f"Context:\n{context}\n\nQ: What is FlowFoundry?\nA:"
    answer = f"[ECHO] {prompt[:200]}..."

    print(
        json.dumps(
            {"collection": coll_name, "hits": len(hits), "answer": answer}, indent=2
        )
    )


if __name__ == "__main__":
    main()
