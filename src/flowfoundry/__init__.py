from __future__ import annotations
import os

from .utils import ping, hello, __version__, load_plugins

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

from .model import (
    HFProvider,
    OpenAIProvider,
    OllamaProvider,
    LangChainProvider,
)
from .plans import run_plan, run_plan_file, run_yaml_file

# ---- NEW: safe discovery on import (EPs, namespaces, local folders) ----------
try:
    from .utils import strategies as _strategies  # noqa: F401

    if os.getenv("FF_DISABLE_AUTODISCOVERY", "").lower() not in ("1", "true", "yes"):
        _strategies.load_entrypoints()  # EPs + namespaces + local raw folders
        _strategies.autoload()  # optional: reads FF_STRATEGY_PACKAGES if set
except Exception:
    # Never fail import due to discovery hiccups
    pass
# -----------------------------------------------------------------------------

__all__ = [
    "__version__",
    # functional
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
    "load_plugins",
    # plans
    "run_plan",
    "run_plan_file",
    "run_yaml_file",
]
