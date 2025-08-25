from __future__ import annotations

from typing import Any, Callable, Dict, List, cast

from ..registry import register_node
from ..strategies.registry import strategies

Chunk = Dict[str, Any]
Hit = Dict[str, Any]


@register_node("strategy.chunking")
class ChunkingStrategyNode:
    def __init__(self, name: str = "recursive", **kwargs: Any) -> None:
        self.name = name
        self.kwargs = kwargs

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Expect a callable like: (text, *, doc_id=..., **kw) -> List[Chunk]
        fn = cast(Callable[..., List[Chunk]], strategies.get("chunking", self.name))

        # Normalise input docs
        docs: List[Dict[str, Any]] = []
        docs_in = state.get("documents")
        if isinstance(docs_in, list):
            docs = cast(List[Dict[str, Any]], docs_in)
        elif "document" in state:
            docs = [
                {
                    "doc_id": cast(str, state.get("doc_id", "doc")),
                    "text": cast(str, state["document"]),
                    "path": "",
                    "metadata": {},
                }
            ]

        chunks: List[Chunk] = []
        for d in docs:
            text = str(d.get("text", "")).strip()
            if not text:
                continue
            doc_id = str(d.get("doc_id", "doc"))
            pieces = fn(text, doc_id=doc_id, **self.kwargs)
            # carry minimal metadata forward
            for ch in pieces:
                ch.setdefault("metadata", {})
                ch["metadata"].setdefault(
                    "doc", d.get("metadata", {}).get("doc", doc_id)
                )
            chunks.extend(pieces)

        state["chunks"] = chunks
        return state


@register_node("strategy.indexing")
class IndexingStrategyNode:
    def __init__(self, name: str, **kwargs: Any) -> None:
        self.name = name
        self.kwargs = kwargs

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Callable like: (chunks, **kw) -> Any (often str collection/index name)
        fn = cast(Callable[..., Any], strategies.get("indexing", self.name))
        result = fn(state.get("chunks", []), **self.kwargs)
        if isinstance(result, str):
            state["index_name"] = result
        return state


@register_node("strategy.retrieve")
class RetrieveStrategyNode:
    def __init__(self, name: str, **kwargs: Any) -> None:
        self.name = name
        self.kwargs = kwargs

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Callable like: (query, **kw) -> List[Hit]
        fn = cast(Callable[..., List[Hit]], strategies.get("retrieve", self.name))
        hits = fn(state.get("query", ""), **self.kwargs)
        state["retrieved"] = hits
        return state


@register_node("strategy.rerank")
class RerankStrategyNode:
    def __init__(self, name: str, **kwargs: Any) -> None:
        self.name = name
        self.kwargs = kwargs

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Callable like: (query, hits, **kw) -> List[Hit]
        fn = cast(Callable[..., List[Hit]], strategies.get("rerank", self.name))
        hits_in = cast(List[Hit], state.get("retrieved", []))
        state["retrieved"] = fn(state.get("query", ""), hits_in, **self.kwargs)
        return state
