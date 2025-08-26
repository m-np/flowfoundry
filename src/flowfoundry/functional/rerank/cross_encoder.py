from __future__ import annotations
from typing import List, Dict, Any, Optional
from ...utils import register_strategy

# Optional dependency with graceful fallback
CrossEncoder: Optional[Any]
try:
    from sentence_transformers import CrossEncoder as _CrossEncoder

    CrossEncoder = _CrossEncoder
except Exception:
    CrossEncoder = None


@register_strategy("rerank", "cross_encoder")
def cross_encoder(
    query: str,
    hits: List[Dict],
    *,
    model: str,
    top_k: int | None = None,
) -> List[Dict]:
    """
    Contract: (query, hits, **kwargs) -> hits
    kwargs:
      - model: sentence-transformers cross-encoder name
      - top_k: keep top_k results after scoring
    """
    if CrossEncoder is None:
        # Dependency missing -> no-op, preserve pipeline
        return hits

    ce = CrossEncoder(model)
    pairs = [(query, h.get("text", "")) for h in hits]
    scores = ce.predict(pairs)
    reranked = [dict(h, score=float(s)) for h, s in zip(hits, scores)]
    reranked.sort(key=lambda x: x.get("score", 0.0), reverse=True)
    return reranked[:top_k] if top_k else reranked
