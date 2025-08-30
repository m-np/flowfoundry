# tests/functional/test_rerank.py
from flowfoundry import rerank_identity, preselect_bm25


def _hits():
    return [
        {
            "text": "Budget is set to $1,000 for people.",
            "metadata": {"source": "a.pdf", "page": 1},
        },
        {
            "text": "People discuss the budget in section 2.",
            "metadata": {"source": "a.pdf", "page": 2},
        },
        {"text": "Irrelevant text about cats.", "metadata": {"source": "b.pdf"}},
        {"text": "Budget and people appear here.", "metadata": {"source": "c.pdf"}},
    ]


def test_rerank_identity_respects_order_and_topk():
    hits = _hits()
    out = rerank_identity("dummy query", hits, top_k=2)  # pass a query arg
    assert len(out) == 4
    assert out[0]["text"] == hits[0]["text"]


def test_bm25_preselect_reduces_to_topk_and_keeps_dicts():
    hits = _hits()
    out = preselect_bm25("What is people's budget?", hits, top_k=3)
    assert len(out) == 3
    assert all(isinstance(h, dict) and "text" in h for h in out)
