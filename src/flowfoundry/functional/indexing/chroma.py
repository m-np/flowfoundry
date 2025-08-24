from __future__ import annotations
from typing import List, Dict, Any, Optional, cast
from ...strategies.registry import register_strategy
from ...exceptions import FFDependencyError

chromadb: Optional[Any]
try:
    import chromadb as _chromadb

    chromadb = _chromadb
except Exception:
    chromadb = None


@register_strategy("indexing", "chroma_upsert")
def chroma_upsert(
    chunks: List[Dict], *, path: str = ".ff_chroma", collection: str = "docs"
) -> str:
    if chromadb is None:
        raise FFDependencyError(
            "Install with `pip install flowfoundry[rag]` for Chroma support"
        )
    client = chromadb.PersistentClient(path=path)
    coll = client.get_or_create_collection(collection)
    ids = [f"{c['doc']}::{i}" for i, c in enumerate(chunks)]
    texts = [str(c["text"]) for c in chunks]
    metas = [
        {"doc": c["doc"], "start": c.get("start"), "end": c.get("end")} for c in chunks
    ]
    coll.upsert(ids=ids, documents=texts, metadatas=metas)
    return cast(str, coll.name)


@register_strategy("indexing", "chroma_query")
def chroma_query(
    query: str, *, k: int = 5, path: str = ".ff_chroma", collection: str = "docs"
) -> List[Dict]:
    if chromadb is None:
        raise FFDependencyError(
            "Install with `pip install flowfoundry[rag]` for Chroma support"
        )
    client = chromadb.PersistentClient(path=path)
    coll = client.get_or_create_collection(collection)
    res = coll.query(query_texts=[query], n_results=k)
    hits = []
    for txt, md, dist in zip(
        res["documents"][0], res["metadatas"][0], res["distances"][0]
    ):
        hits.append({"text": txt, "metadata": md, "score": float(dist)})
    return hits
