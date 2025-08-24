from __future__ import annotations
from flowfoundry.blocks.core import make_block_class
from flowfoundry.functional.indexing import (
    qdrant_upsert as _upsert,
    qdrant_query as _query,
)

QdrantUpsert = make_block_class(
    "QdrantUpsert",
    _upsert,
    doc="QdrantUpsert(url, collection, dim) → collection name. Delegates to functional.indexing.qdrant_upsert.",
)

QdrantQuery = make_block_class(
    "QdrantQuery",
    _query,
    doc="QdrantQuery(url, collection, k, vector=None) → hits. Delegates to functional.indexing.qdrant_query.",
)
