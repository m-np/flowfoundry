from typing import Protocol, Dict, Any, List

STRATEGY_CONTRACT_VERSION = "1.0"


class ChunkingFn(Protocol):
    def __call__(
        self, text: str, *, doc_id: str = "doc", **kwargs: Any
    ) -> List[Dict[str, Any]]: ...


class IndexUpsertFn(Protocol):
    def __call__(self, chunks: List[Dict[str, Any]], **kwargs: Any) -> str: ...


class IndexQueryFn(Protocol):
    def __call__(self, query: str, **kwargs: Any) -> List[Dict[str, Any]]: ...


class RerankFn(Protocol):
    def __call__(
        self, query: str, hits: List[Dict[str, Any]], **kwargs: Any
    ) -> List[Dict[str, Any]]: ...
