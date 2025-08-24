from __future__ import annotations
from flowfoundry.blocks.core import make_block_class
from flowfoundry.functional.indexing import (
    chroma_upsert as _upsert,
    chroma_query as _query,
)

ChromaUpsert = make_block_class(
    "ChromaUpsert",
    _upsert,
    doc="ChromaUpsert(path, collection) → index name. Delegates to functional.indexing.chroma_upsert.",
)

ChromaQuery = make_block_class(
    "ChromaQuery",
    _query,
    doc="ChromaQuery(path, collection, k) → hits. Delegates to functional.indexing.chroma_query.",
)
