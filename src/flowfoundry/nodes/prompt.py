from __future__ import annotations
from typing import Dict, Any
from ..registry import register_node


@register_node("prompt.rag")
class RagPromptNode:
    def __init__(self): ...
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        ctx = "\n\n".join(h["text"] for h in state.get("retrieved", []))
        q = state.get("query", "")
        state["prompt"] = (
            f"You are a helpful assistant.\nContext:\n{ctx}\n\nQuestion: {q}\nAnswer:"
        )
        return state
