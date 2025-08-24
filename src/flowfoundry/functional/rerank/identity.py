from __future__ import annotations
from typing import List, Dict
from ...strategies.registry import register_strategy


@register_strategy("rerank", "identity")
def identity(query: str, hits: List[Dict], **_) -> List[Dict]:
    return hits
