from .utils import (
    ping,
    hello,
    __version__,
)

from .functional import (
    chunk_fixed,
    chunk_recursive,
    chunk_hybrid,
    index_chroma_upsert,
    index_chroma_query,
    rerank_identity,
    rerank_cross_encoder,
    preselect_bm25,
    compose_llm,
    pdf_loader,
)

from .model import HFProvider, OpenAIProvider, OllamaProvider, LangChainProvider

__all__ = [
    "__version__",
    # functional (stable names)
    "chunk_fixed",
    "chunk_recursive",
    "chunk_hybrid",
    "index_chroma_upsert",
    "index_chroma_query",
    "rerank_identity",
    "rerank_cross_encoder",
    "preselect_bm25",
    "compose_llm",
    "pdf_loader",
    # providers
    "HFProvider",
    "OpenAIProvider",
    "OllamaProvider",
    "LangChainProvider",
    # utils
    "ping",
    "hello",
]
