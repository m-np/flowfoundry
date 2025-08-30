# examples/04_compose_ollama.py
from flowfoundry import index_chroma_query, preselect_bm25, compose_llm

CHROMA_PATH = ".ff_chroma"
COLLECTION = "docs"
QUESTION = "What is people's budget?"


def main():
    hits = index_chroma_query(QUESTION, path=CHROMA_PATH, collection=COLLECTION, k=8)
    hits = preselect_bm25(QUESTION, hits, top_k=5)

    answer = compose_llm(
        QUESTION,
        hits,
        provider="ollama",
        model="llama3:8b",
        host="http://localhost:11434",
        max_tokens=400,
        reuse_provider=True,
    )
    print("\n=== Answer (Ollama) ===\n")
    print(answer)


if __name__ == "__main__":
    main()
