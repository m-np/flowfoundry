from __future__ import annotations
from flowfoundry.blocks.core import make_block_class
from flowfoundry.functional.rerank import cross_encoder as _ce

CrossEncoder = make_block_class(
    "CrossEncoder",
    _ce,
    doc="CrossEncoder(model, top_k) → reranked hits. Delegates to functional.rerank.cross_encoder.",
)
