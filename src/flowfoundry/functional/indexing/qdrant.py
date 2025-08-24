from __future__ import annotations
from typing import List, Dict, Any, Optional
from ...strategies.registry import register_strategy
from ...exceptions import FFDependencyError

# Optional dependency with graceful fallback
QdrantClient: Optional[Any]
PointStruct: Optional[Any]
Distance: Optional[Any]
VectorParams: Optional[Any]
try:
    from qdrant_client import QdrantClient as _QdrantClient
    from qdrant_client.http.models import (
        PointStruct as _PointStruct,
        Distance as _Distance,
        VectorParams as _VectorParams,
    )

    QdrantClient, PointStruct, Distance, VectorParams = (
        _QdrantClient,
        _PointStruct,
        _Distance,
        _VectorParams,
    )
except Exception:
    QdrantClient = PointStruct = Distance = VectorParams = None


@register_strategy("indexing", "qdrant_upsert")
def qdrant_upsert(
    chunks: List[Dict],
    *,
    url: str = "http://localhost:6333",
    collection: str = "docs",
    dim: int | None = None,
) -> str:
    if (
        QdrantClient is None
        or VectorParams is None
        or Distance is None
        or PointStruct is None
    ):
        raise FFDependencyError(
            "Install with `pip install flowfoundry[qdrant]` for Qdrant support"
        )
    client = QdrantClient(url=url)
    if dim is None:
        first = next((c for c in chunks if c.get("embedding") is not None), None)
        dim = len(first["embedding"]) if first is not None else 384
    try:
        client.get_collection(collection)
    except Exception:
        client.recreate_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )
    points = []
    for i, c in enumerate(chunks):
        vec = c.get("embedding")
        if vec is None:
            continue
        points.append(
            PointStruct(
                id=i, vector=vec, payload={"doc": c.get("doc"), "text": c.get("text")}
            )
        )
    if points:
        client.upsert(collection_name=collection, points=points)
    return collection


@register_strategy("indexing", "qdrant_query")
def qdrant_query(
    query: str,
    *,
    url: str = "http://localhost:6333",
    collection: str = "docs",
    k: int = 5,
    vector: List[float] | None = None,
) -> List[Dict]:
    if QdrantClient is None:
        raise FFDependencyError(
            "Install with `pip install flowfoundry[qdrant]` for Qdrant support"
        )
    client = QdrantClient(url=url)
    if vector is None:
        return []
    res = client.search(collection_name=collection, query_vector=vector, limit=k)
    return [
        {
            "text": r.payload.get("text"),
            "metadata": {"doc": r.payload.get("doc")},
            "score": float(r.score),
        }
        for r in res
    ]
