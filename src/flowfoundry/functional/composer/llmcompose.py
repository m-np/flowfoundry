from __future__ import annotations
from typing import Any, List, Dict
from ...utils import register_strategy, get_llm_provider, get_llm_cached, FFConfigError


def _format_context(hits: List[Dict[str, Any]], max_chars: int) -> str:
    out: List[str] = []
    used = 0
    for h in hits:
        text = (h.get("text") or "").strip()
        meta = h.get("metadata") or {}
        source = meta.get("source") or meta.get("doc") or "source"
        page = meta.get("page")
        cite = f"[{source}:{page}]" if page is not None else f"[{source}]"
        if not text:
            continue
        block = f"{cite} {text}"
        if used + len(block) > max_chars and out:
            break
        out.append(block)
        used += len(block)
    return "\n\n".join(out)


def _compose_prompt(question: str, context: str) -> Dict[str, str]:
    system = (
        "You are a careful assistant. Answer ONLY from the provided context. "
        "If the answer is not in the context, say you don't know. "
        "Cite sources inline using the bracket tags that precede each passage."
        "Instructions:\n"
        "- Provide a concise answer.\n"
        "- Include short inline citations like [source.pdf:3] where relevant.\n"
        "- If uncertain, say you don't know.\n"
    )
    user = f"Question: {question}\n\n" f"Context:\n{context}\n\n"
    return {"system": system, "user": user}


@register_strategy("compose", "llm")
def compose_llm(
    question: str,
    hits: List[Dict[str, Any]],
    *,
    provider: str,
    model: str,
    max_context_chars: int = 6000,
    max_tokens: int = 512,
    reuse_provider: bool = True,  # <--- NEW: toggle caching behavior
    **provider_kwargs: Any,  # e.g., api_key, host, device, backend
) -> str:
    if not provider or not model:
        raise FFConfigError("compose_llm requires 'provider' and 'model'.")
    context = _format_context(hits, max_chars=max_context_chars)
    if not context:
        return "I couldn't find relevant context to answer the question."

    prompt = _compose_prompt(question, context)

    ctor_kwargs = {"model": model, **provider_kwargs}

    if reuse_provider:
        llm = get_llm_cached(provider, **ctor_kwargs)
    else:
        # one-off instance (no cache)
        ProviderCls = get_llm_provider(provider)
        llm = ProviderCls(**ctor_kwargs)

    return llm.generate(
        system=prompt["system"], user=prompt["user"], max_tokens=max_tokens
    )
