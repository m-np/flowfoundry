from __future__ import annotations
from typing import Dict, Any
from ..registry import register_node
from ..strategies.registry import strategies


@register_node("strategy.chunking")
class ChunkingStrategyNode:
    def __init__(self, name: str = "recursive", **kwargs):
        self.name = name
        self.kwargs = kwargs

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        fn = strategies.get("chunking", self.name)
        text = state.get("document") or state.get("text")
        doc_id = state.get("doc_id", "doc")
        state["chunks"] = fn(text, doc_id=doc_id, **self.kwargs)
        return state


@register_node("strategy.indexing")
class IndexingStrategyNode:
    def __init__(self, name: str = "chroma_upsert", **kwargs):
        self.name = name
        self.kwargs = kwargs

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        fn = strategies.get("indexing", self.name)
        idx = fn(state["chunks"], **self.kwargs)
        state["index_name"] = idx
        return state


@register_node("strategy.retrieve")
class RetrieveStrategyNode:
    def __init__(self, name: str = "chroma_query", **kwargs):
        self.name = name
        self.kwargs = kwargs

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        fn = strategies.get("indexing", self.name)
        state["retrieved"] = fn(state["query"], **self.kwargs)
        return state


@register_node("strategy.rerank")
class RerankStrategyNode:
    def __init__(self, name: str = "identity", **kwargs):
        self.name = name
        self.kwargs = kwargs

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        fn = strategies.get("rerank", self.name)
        state["retrieved"] = fn(
            state.get("query", ""), state.get("retrieved", []), **self.kwargs
        )
        return state
