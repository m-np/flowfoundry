from flowfoundry.blocks import Recursive, BM25, Identity
from flowfoundry.functional import chunk_recursive, preselect_bm25, rerank_identity
from flowfoundry.integrity import assert_single_source_of_truth


def test_blocks_are_wrappers():
    assert_single_source_of_truth()


def test_chunking_equivalence():
    text = "a " * 1200
    chunks_block = Recursive(size=200, overlap=50)(text, doc_id="d1")
    chunks_func = chunk_recursive(text, size=200, overlap=50, doc_id="d1")
    assert [c["text"] for c in chunks_block] == [c["text"] for c in chunks_func]


def test_rerank_equivalence_identity_and_bm25():
    q = "hello world"
    hits = [
        {"text": "hello world one"},
        {"text": "world of hello"},
        {"text": "unrelated"},
    ]
    assert Identity()(q, hits) == rerank_identity(q, hits)
    assert BM25(top_k=2)(q, hits) == preselect_bm25(q, hits, top_k=2)
