from __future__ import annotations
from .blocks.core import StrategyBlock
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


def assert_single_source_of_truth() -> None:
    """Ensure all Blocks are thin wrappers over functional strategies."""
    for cls in [
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
    ]:
        if not issubclass(cls, StrategyBlock):
            raise AssertionError(
                f"{cls.__name__} must derive from StrategyBlock (wrapper over functional)."
            )
