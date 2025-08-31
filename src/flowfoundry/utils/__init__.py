"""
flowfoundry.utils

Utility layer for shared exceptions, contracts, and versioning.
This module is imported by both functional and model code.
"""

from .exceptions import (
    FFError,
    FFConfigError,
    FFRegistryError,
    FFDependencyError,
    FFExecutionError,
    FFIngestionError,
)

from .functional_contracts import (
    STRATEGY_CONTRACT_VERSION,
    IngestionFn,
    ChunkingFn,
    IndexUpsertFn,
    IndexQueryFn,
    RerankFn,
    Chunk,
    InDoc,
    ComposeFn,
)

from .functional_registry import (
    strategies,
    register_strategy,
    strategy_contract_version,
)

from .llm_registry import (
    register_llm_provider,
    get_llm_provider,
    get_llm_cached,
    clear_llm_cache,
)

from .llm_contracts import (
    LLMProvider,
)

from .versions import __version__

from .plugin_loader import load_plugins

# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------


def ping() -> str:
    """Lightweight health check."""
    return "flowfoundry: ok"


def hello(name: str = "world") -> str:
    """Simple greeting helper."""
    return f"hello, {name}!"


__all__ = [
    # Exceptions
    "FFError",
    "FFConfigError",
    "FFRegistryError",
    "FFDependencyError",
    "FFExecutionError",
    "FFIngestionError",
    # Functional Contracts
    "STRATEGY_CONTRACT_VERSION",
    "IngestionFn",
    "ChunkingFn",
    "IndexUpsertFn",
    "IndexQueryFn",
    "RerankFn",
    "Chunk",
    "InDoc",
    "ComposeFn",
    # Functional Registry
    "strategies",
    "register_strategy",
    "strategy_contract_version",
    # LLM Registry
    "register_llm_provider",
    "get_llm_provider",
    "get_llm_cached",
    "clear_llm_cache",
    # LLM Contracts
    "LLMProvider",
    # Version
    "__version__",
    # Helpers
    "ping",
    "hello",
    # Plugin Loader
    "load_plugins",
]
