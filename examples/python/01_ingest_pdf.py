"""
Ingest a PDF into a local Chroma collection using programmatic workflow nodes.
Runs offline. Uses pkg:sample.pdf (or graceful fallback text).
"""

from __future__ import annotations
import json
from flowfoundry.config import WorkflowSpec, NodeSpec, EdgeSpec
from flowfoundry.graphs.builder import compile_workflow


def main() -> None:
    spec = WorkflowSpec(
        start="load",
        nodes=[
            NodeSpec(id="load", type="io.pdf_load", params={"path": "docs/sample.pdf"}),
            NodeSpec(
                id="chunk",
                type="strategy.chunking",
                params={"name": "recursive", "size": 900, "overlap": 120},
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

    graph = compile_workflow(spec)
    state = graph.invoke({})
    print(json.dumps({k: state.get(k) for k in ["doc_id", "index_name"]}, indent=2))
    print("✓ Ingestion complete.")


if __name__ == "__main__":
    main()
