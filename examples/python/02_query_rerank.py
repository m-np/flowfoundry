# examples/02_query_rerank.py
from flowfoundry import (
    index_chroma_query,
    preselect_bm25,
)  # or rerank_identity / rerank_cross_encoder

CHROMA_PATH = ".ff_chroma"
COLLECTION = "docs"
QUESTION = "What is people's budget?"


def main():
    hits = index_chroma_query(QUESTION, path=CHROMA_PATH, collection=COLLECTION, k=8)
    print(f"[query] initial hits = {len(hits)}")

    hits = preselect_bm25(
        QUESTION, hits, top_k=5
    )  # swap for rerank_identity(...) or rerank_cross_encoder(...)
    print(f"[rerank] final hits = {len(hits)}")

    # show a few
    for i, h in enumerate(hits[:5], 1):
        text = (h.get("text") or "").replace("\n", " ")
        print(f"{i:02d}. {text[:160]}{'…' if len(text) > 160 else ''}")


if __name__ == "__main__":
    main()
