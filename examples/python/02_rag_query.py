"""
End-to-end RAG:
1) Ingest pkg:sample.pdf (fast if already indexed)
2) Query, preselect with BM25 (no cross-encoder required)
3) Build prompt and answer via echo provider (offline)

If you want OpenAI: install extras and set provider="openai".
"""

from __future__ import annotations
import json
from flowfoundry.config import WorkflowSpec, NodeSpec, EdgeSpec
from flowfoundry.graphs.builder import compile_workflow


def build_ingest_spec() -> WorkflowSpec:
    return WorkflowSpec(
        start="load",
        nodes=[
            NodeSpec(id="load", type="io.pdf_load", params={"path": "pkg:sample.pdf"}),
            NodeSpec(
                id="chunk",
                type="strategy.chunking",
                params={"name": "recursive", "size": 800, "overlap": 80},
            ),
            NodeSpec(
                id="upsert",
                type="strategy.indexing",
                params={
                    "name": "chroma_upsert",
                    "path": ".ff_chroma",
                    "collection": "docs",
                },
            ),
        ],
        edges=[
            EdgeSpec(source="load", target="chunk"),
            EdgeSpec(source="chunk", target="upsert"),
        ],
    )


def build_rag_spec() -> WorkflowSpec:
    return WorkflowSpec(
        start="retrieve",
        nodes=[
            NodeSpec(
                id="retrieve",
                type="strategy.retrieve",
                params={
                    "name": "chroma_query",
                    "path": ".ff_chroma",
                    "collection": "docs",
                    "k": 8,
                },
            ),
            NodeSpec(
                id="bm25",
                type="strategy.rerank",
                params={"name": "bm25_preselect", "top_k": 8},
            ),
            NodeSpec(id="prompt", type="prompt.rag", params={}),
            NodeSpec(
                id="answer",
                type="llm.chat",
                params={"provider": "echo", "model": "gpt-4o-mini"},
            ),
        ],
        edges=[
            EdgeSpec(source="retrieve", target="bm25"),
            EdgeSpec(source="bm25", target="prompt"),
            EdgeSpec(source="prompt", target="answer"),
        ],
    )


def main() -> None:
    # 1) Ingest (idempotent)
    compile_workflow(build_ingest_spec()).invoke({})

    # 2) Run RAG
    question = "Summarize the economic growth."
    out = compile_workflow(build_rag_spec()).invoke({"query": question})
    print(json.dumps({"question": question, "answer": out.get("answer", "")}, indent=2))


if __name__ == "__main__":
    main()
