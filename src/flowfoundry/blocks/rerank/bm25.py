from __future__ import annotations
from flowfoundry.blocks.core import make_block_class
from flowfoundry.functional.rerank import bm25_preselect as _bm25

BM25 = make_block_class(
    "BM25",
    _bm25,
    doc="BM25(top_k) → preselected hits. Delegates to functional.rerank.bm25_preselect.",
)
