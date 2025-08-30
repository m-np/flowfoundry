# examples/05_langchain_backends.py
from flowfoundry import index_chroma_query, preselect_bm25, compose_llm

CHROMA_PATH = ".ff_chroma"
COLLECTION = "docs"
QUESTION = "What is people's budget?"


def main():
    hits = index_chroma_query(QUESTION, path=CHROMA_PATH, collection=COLLECTION, k=8)
    hits = preselect_bm25(QUESTION, hits, top_k=5)

    # LangChain + Ollama
    ans_ollama = compose_llm(
        QUESTION,
        hits,
        provider="langchain",
        model="llama3:8b",
        backend="ollama",
        host="http://localhost:11434",
        max_tokens=400,
    )
    print("\n=== LangChain (Ollama backend) ===\n")
    print(ans_ollama)

    # LangChain + OpenAI
    ans_openai = compose_llm(
        QUESTION,
        hits,
        provider="langchain",
        model="gpt-4o-mini",
        backend="openai",
        max_tokens=400,
        reuse_provider=True,
    )
    print("\n=== LangChain (OpenAI backend) ===\n")
    print(ans_openai)


if __name__ == "__main__":
    main()
