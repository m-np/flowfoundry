from typing import Protocol, Dict, Any, List, Union
from pathlib import Path

from .versions import __version__

STRATEGY_CONTRACT_VERSION = __version__

Chunk = Dict[str, Any]
InDoc = Dict[str, Any]


class IngestionFn(Protocol):
    def __call__(self, path: Union[str, Path], **kwargs: Any) -> List[InDoc]: ...


class ChunkingFn(Protocol):
    def __call__(
        self, data: Union[str, List[InDoc]], *, doc_id: str = "doc", **kwargs: Any
    ) -> List[Chunk]: ...


class IndexUpsertFn(Protocol):
    def __call__(self, chunks: List[Chunk], **kwargs: Any) -> str: ...


class IndexQueryFn(Protocol):
    def __call__(self, query: str, **kwargs: Any) -> List[Dict[str, Any]]: ...


class RerankFn(Protocol):
    def __call__(
        self, query: str, hits: List[Dict[str, Any]], **kwargs: Any
    ) -> List[Dict[str, Any]]: ...
