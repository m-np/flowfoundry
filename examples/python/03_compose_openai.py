# examples/03_compose_openai.py
import os
from flowfoundry import index_chroma_query, preselect_bm25, compose_llm

CHROMA_PATH = ".ff_chroma"
COLLECTION = "docs"
QUESTION = "What is people's budget?"


def main():
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Set OPENAI_API_KEY before running this example.")

    hits = index_chroma_query(QUESTION, path=CHROMA_PATH, collection=COLLECTION, k=8)
    hits = preselect_bm25(QUESTION, hits, top_k=5)

    answer = compose_llm(
        QUESTION,
        hits,
        provider="openai",
        model="gpt-4o-mini",
        max_tokens=400,
        reuse_provider=True,
    )
    print("\n=== Answer (OpenAI) ===\n")
    print(answer)


if __name__ == "__main__":
    main()
