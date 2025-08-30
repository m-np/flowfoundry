# tests/functional/test_indexing_chroma.py
import importlib.util
import pytest
from flowfoundry import index_chroma_upsert, index_chroma_query

chromadb_available = importlib.util.find_spec("chromadb") is not None

pytestmark = pytest.mark.skipif(
    not chromadb_available,
    reason="chromadb not installed; install with flowfoundry[rag]",
)


def test_index_and_query_roundtrip(tmp_path):
    path = tmp_path / ".ff_chroma"
    collection = "docs"
    chunks = [
        {
            "doc": "a",
            "chunk_index": 0,
            "text": "People's budget is $1,000.",
            "metadata": {"source": "a.pdf", "page": 1},
        },
        {
            "doc": "a",
            "chunk_index": 1,
            "text": "Budget is discussed in section 2.",
            "metadata": {"source": "a.pdf", "page": 2},
        },
    ]
    index_chroma_upsert(chunks, path=str(path), collection=collection)
    hits = index_chroma_query(
        "people budget", path=str(path), collection=collection, k=5
    )
    assert isinstance(hits, list) and len(hits) >= 1
    assert any("budget" in h.get("text", "").lower() for h in hits)
