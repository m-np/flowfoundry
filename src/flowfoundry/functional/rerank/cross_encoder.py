from __future__ import annotations
from typing import List, Dict, Any, Optional
from ...strategies.registry import register_strategy

# Optional dependency, keep runtime fallback without type ignores
CrossEncoder: Optional[Any]
try:
    from sentence_transformers import CrossEncoder as _CrossEncoder

    CrossEncoder = _CrossEncoder
except Exception:
    CrossEncoder = None


@register_strategy("rerank", "cross_encoder")
def cross_encoder(
    model: str, query: str, hits: List[Dict], top_k: int | None = None
) -> List[Dict]:
    ce_cls = CrossEncoder
    if ce_cls is None:
        return hits
    ce = ce_cls(model)  # ce_cls is Any at type-check time
    pairs = [(query, h.get("text", "")) for h in hits]
    scores = ce.predict(pairs)
    reranked = [dict(h, score=float(s)) for h, s in zip(hits, scores)]
    reranked.sort(key=lambda x: x.get("score", 0.0), reverse=True)
    return reranked[:top_k] if top_k else reranked
