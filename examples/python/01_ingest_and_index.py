# examples/01_load_chunk_index.py
from flowfoundry import pdf_loader, chunk_hybrid, index_chroma_upsert

DOCS_DIR = "docs/samples/"
CHROMA_PATH = ".ff_chroma"
COLLECTION = "docs"


def main():
    pages = pdf_loader(DOCS_DIR)
    print(f"[load] pages = {len(pages)}")

    chunks = chunk_hybrid(pages, chunk_size=500, chunk_overlap=50)
    print(f"[chunk] chunks = {len(chunks)}")

    index_chroma_upsert(chunks, path=CHROMA_PATH, collection=COLLECTION)
    print(f"[index] upserted {len(chunks)} chunks → {CHROMA_PATH}:{COLLECTION}")


if __name__ == "__main__":
    main()
