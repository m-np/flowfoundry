from .version import __version__
from .registry import (
    registries,
    register_entrypoints,
    register_node,
    register_workflow,
    register_memory,
    register_model,
)
from .strategies.registry import (
    strategies,
    register_strategy,
    strategy_contract_version,
)
from .functional import (
    chunk_fixed,
    chunk_recursive,
    chunk_hybrid,
    index_chroma_upsert,
    index_chroma_query,
    index_qdrant_upsert,
    index_qdrant_query,
    rerank_identity,
    rerank_cross_encoder,
    preselect_bm25,
)
from .utils import ping, hello

# Explicit imports to satisfy Ruff (avoid F403)
from .blocks import (
    Fixed,
    Recursive,
    Hybrid,
    ChromaUpsert,
    ChromaQuery,
    QdrantUpsert,
    QdrantQuery,
    Identity,
    CrossEncoder,
    BM25,
)

__all__ = [
    "__version__",
    # registry
    "registries",
    "register_entrypoints",
    "register_node",
    "register_workflow",
    "register_memory",
    "register_model",
    # strategies
    "strategies",
    "register_strategy",
    "strategy_contract_version",
    # functional (stable names)
    "chunk_fixed",
    "chunk_recursive",
    "chunk_hybrid",
    "index_chroma_upsert",
    "index_chroma_query",
    "index_qdrant_upsert",
    "index_qdrant_query",
    "rerank_identity",
    "rerank_cross_encoder",
    "preselect_bm25",
    # blocks (ergonomic wrappers)
    "Fixed",
    "Recursive",
    "Hybrid",
    "ChromaUpsert",
    "ChromaQuery",
    "QdrantUpsert",
    "QdrantQuery",
    "Identity",
    "CrossEncoder",
    "BM25",
    # utils
    "ping",
    "hello",
]
