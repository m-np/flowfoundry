from __future__ import annotations
from typing import List, Dict, Tuple, Any, Optional
from ...utils import register_strategy

BM25Okapi: Optional[Any]
try:
    from rank_bm25 import BM25Okapi as _BM25Okapi

    BM25Okapi = _BM25Okapi
except Exception:
    BM25Okapi = None


@register_strategy("rerank", "bm25_preselect")
def bm25_preselect(query: str, hits: List[Dict], top_k: int = 20) -> List[Dict]:
    if BM25Okapi is None:
        return hits[:top_k]
    corpus = [h.get("text", "") for h in hits]
    tokenized = [c.split() for c in corpus]
    bm25 = BM25Okapi(tokenized)
    scores = bm25.get_scores(query.split())
    paired: List[Tuple[int, float]] = list(enumerate(scores))
    paired.sort(key=lambda x: x[1], reverse=True)
    idxs = [i for i, _ in paired[:top_k]]
    return [hits[i] for i in idxs]
