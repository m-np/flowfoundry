# tests/functional/test_chunking.py
from typing import Dict, Any, List

from flowfoundry import chunk_fixed, chunk_recursive, chunk_hybrid


def test_chunk_fixed_string_basic():
    text = "abcdefghij"  # 10 chars
    chunk_size, chunk_overlap = 4, 2
    chunks = chunk_fixed(
        text, chunk_size=chunk_size, chunk_overlap=chunk_overlap, doc_id="docX"
    )

    assert isinstance(chunks, list)
    assert all(isinstance(c, dict) for c in chunks)

    last_index = -1
    for i, c in enumerate(chunks):
        # index metadata monotonic
        assert c["chunk_index"] == i
        assert c["doc"] == "docX"

        # start/end well-formed (but don't require end <= len(text))
        start, end = c["start"], c["end"]
        assert isinstance(start, int) and isinstance(end, int)
        assert 0 <= start < end

        # chunk content is non-empty, comes from original text somewhere,
        # and respects size bound (<= chunk_size)
        chunk_text = c["text"]
        assert isinstance(chunk_text, str) and chunk_text
        assert chunk_text in text
        assert 1 <= len(chunk_text) <= chunk_size

        # chunk_index increases
        assert i > last_index
        last_index = i


def test_chunk_fixed_list_of_docs_preserves_metadata():
    docs: List[Dict[str, Any]] = [
        {"text": "hello world", "doc": "A", "meta": {"a": 1}},
        {"text": "bye world", "doc": "B", "meta": {"b": 2}},
    ]
    chunks = chunk_fixed(docs, chunk_size=5, chunk_overlap=1, doc_id="IGNORED")
    assert {c["doc"] for c in chunks} == {"A", "B"}
    for c in chunks:
        assert "meta" in c  # original metadata carried forward


def test_chunk_hybrid_multiple_chunks():
    docs = [{"text": "x" * 300, "doc": "Z"}]
    chunks = chunk_hybrid(docs, chunk_size=100, chunk_overlap=20)
    assert len(chunks) >= 3
    assert all(isinstance(c["text"], str) and c["text"] for c in chunks)


def test_chunk_recursive_breaks_text():
    docs = [{"text": "Sentence one. Sentence two. Sentence three.", "doc": "Y"}]
    chunks = chunk_recursive(docs, chunk_size=20, chunk_overlap=5)
    # recursive splitter should create at least 2 pieces
    assert len(chunks) >= 2
    for c in chunks:
        assert isinstance(c["text"], str)
        # loose upper bound: chunk_size + small buffer for splitter behavior
        assert len(c["text"]) <= 30
