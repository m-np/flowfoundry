from __future__ import annotations
from typing import Dict, Any, Optional, Callable
from ..registry import register_node

# Narrow the optional import with a precise type so mypy can reason about it
init_chat_model: Optional[Callable[..., Any]]
try:
    from langchain.chat_models import init_chat_model as _init_chat_model

    init_chat_model = _init_chat_model
except Exception:
    init_chat_model = None


@register_node("llm.chat")
class LLMChatNode:
    def __init__(self, model: str = "gpt-4o-mini", provider: str = "openai"):
        self.model = model
        self.provider = provider

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        prompt = state.get("prompt")
        if not prompt:
            raise ValueError("prompt missing in state")

        fn = init_chat_model  # local alias allows mypy to narrow Optional
        if fn is None:
            state["answer"] = f"[ECHO:{self.model}] {prompt[:300]}"
            return state

        llm = fn(self.model, model_provider=self.provider)
        rsp = llm.invoke(prompt)
        state["answer"] = getattr(rsp, "content", str(rsp))
        return state
