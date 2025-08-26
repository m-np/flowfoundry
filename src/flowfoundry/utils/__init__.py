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
)

from .functional_registry import (
    strategies,
    register_strategy,
    strategy_contract_version,
)

from .versions import __version__


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
    # Functional Registry
    "strategies",
    "register_strategy",
    "strategy_contract_version",
    # Version
    "__version__",
    # Helpers
    "ping",
    "hello",
]
