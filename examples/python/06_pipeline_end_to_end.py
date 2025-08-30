# examples/06_pipeline_end_to_end.py
import os
from flowfoundry import (
    pdf_loader,
    chunk_hybrid,  # swap to chunk_fixed / chunk_recursive if you like
    index_chroma_upsert,
    index_chroma_query,
    preselect_bm25,  # or rerank_identity / rerank_cross_encoder
    compose_llm,
)

DOCS_DIR = "docs/samples/"
CHROMA_PATH = ".ff_chroma"
COLLECTION = "docs"
QUESTION = "What is people's budget?"


def main():
    if not os.getenv("OPENAI_API_KEY"):
        print(
            "[warn] OPENAI_API_KEY not set; switch provider in compose_llm call if needed."
        )

    pages = pdf_loader(DOCS_DIR)
    print(f"[load] pages = {len(pages)}")

    chunks = chunk_hybrid(pages, chunk_size=500, chunk_overlap=50)
    print(f"[chunk] chunks = {len(chunks)}")

    index_chroma_upsert(chunks, path=CHROMA_PATH, collection=COLLECTION)
    print(f"[index] upserted {len(chunks)} → {CHROMA_PATH}:{COLLECTION}")

    hits = index_chroma_query(QUESTION, path=CHROMA_PATH, collection=COLLECTION, k=8)
    hits = preselect_bm25(QUESTION, hits, top_k=5)
    print(f"[retrieve] hits = {len(hits)}")

    answer = compose_llm(
        QUESTION,
        hits,
        provider="openai",  # change to "ollama" or "langchain" if preferred
        model="gpt-4o-mini",
        max_tokens=400,
        reuse_provider=True,
    )
    print("\n=== Final Answer ===\n")
    print(answer)


if __name__ == "__main__":
    main()
