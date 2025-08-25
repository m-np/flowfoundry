"""
Custom strategy + use it inside a workflow via the generic strategy node.
Adds a tiny reranker that prefers longer passages.
"""

from __future__ import annotations
import json
from typing import List, Dict
from flowfoundry.strategies.registry import register_strategy
from flowfoundry.config import WorkflowSpec, NodeSpec, EdgeSpec
from flowfoundry.graphs.builder import compile_workflow

# --- Custom strategy (registered at import time) ---------------------------------


@register_strategy("rerank", "length_boost")
def length_boost(
    query: str, hits: List[Dict], *, weight: float = 1.0, top_k: int | None = None
) -> List[Dict]:
    scored = []
    for h in hits:
        base = float(h.get("score", 0.0))
        extra = len(h.get("text", "")) / 1000.0
        scored.append(dict(h, score=base + weight * extra))
    scored.sort(key=lambda x: x.get("score", 0.0), reverse=True)
    return scored[:top_k] if top_k else scored


# --- Programmatic workflow using the custom strategy -----------------------------


def build_spec() -> WorkflowSpec:
    return WorkflowSpec(
        start="retrieve",
        nodes=[
            NodeSpec(
                id="ingest_load", type="io.pdf_load", params={"path": "pkg:sample.pdf"}
            ),
            NodeSpec(
                id="ingest_chunk",
                type="strategy.chunking",
                params={"name": "recursive", "size": 800, "overlap": 80},
            ),
            NodeSpec(
                id="ingest_upsert",
                type="strategy.indexing",
                params={
                    "name": "chroma_upsert",
                    "path": ".ff_chroma_len",
                    "collection": "docs_len",
                },
            ),
            NodeSpec(
                id="retrieve",
                type="strategy.retrieve",
                params={
                    "name": "chroma_query",
                    "path": ".ff_chroma_len",
                    "collection": "docs_len",
                    "k": 12,
                },
            ),
            NodeSpec(
                id="boost",
                type="strategy.rerank",
                params={"name": "length_boost", "weight": 2.0, "top_k": 6},
            ),
            NodeSpec(id="prompt", type="prompt.rag", params={}),
            NodeSpec(id="answer", type="llm.chat", params={"provider": "echo"}),
        ],
        edges=[
            EdgeSpec(source="ingest_load", target="ingest_chunk"),
            EdgeSpec(source="ingest_chunk", target="ingest_upsert"),
            EdgeSpec(source="ingest_upsert", target="retrieve"),
            EdgeSpec(source="retrieve", target="boost"),
            EdgeSpec(source="boost", target="prompt"),
            EdgeSpec(source="prompt", target="answer"),
        ],
    )


def main() -> None:
    spec = build_spec()
    out = compile_workflow(spec).invoke({"query": "Outline the main ideas."})
    print(json.dumps({"answer": out.get("answer", "")}, indent=2))


if __name__ == "__main__":
    main()
