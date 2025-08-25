# FlowFoundry

*A strategy-first, cloud-agnostic framework for LLM workflows.*  
Compose chunking, indexing, retrieval, reranking, and agentic flows — with **Keras-like ergonomics** over LangChain / LangGraph.

---

## ✨ Features

- **Strategies**: chunking, indexing, retrieval, reranking  
- **Functional API**: call strategies directly as Python functions  
- **Blocks API**: compose strategies like layers  
- **Nodes & Graphs**: LangGraph-backed workflows (YAML or Python)  
- **Extensible**: register custom strategies or nodes  

---

## Installation

Core only:

```bash
pip install flowfoundry
```

With extras:
```bash
pip install "flowfoundry[rag,search,rerank,qdrant,openai,llm-openai]"
```

Extras include: chromadb, qdrant-client, sentence-transformers, rank-bm25, openai, etc.
All examples run offline by default (echo LLM). Missing deps no-op gracefully.

Sanity check:
```python
from flowfoundry import ping, hello
print(ping())          # -> "flowfoundry: ok"
print(hello("there"))  # -> "hello, there!"
```

## Quickstart (Functional API)

```python
from flowfoundry.functional import (
  chunk_recursive, index_chroma_upsert, index_chroma_query, preselect_bm25
)

text   = "FlowFoundry lets you mix strategies to build RAG."
chunks = chunk_recursive(text, size=120, overlap=20, doc_id="demo")

# Index & query (requires chromadb extra)
index_chroma_upsert(chunks, path=".ff_chroma", collection="docs")
hits = index_chroma_query("What is FlowFoundry?", path=".ff_chroma", collection="docs", k=8)

# Optional rerank (requires rank-bm25)
hits = preselect_bm25("What is FlowFoundry?", hits, top_k=5)

print(hits[0]["text"])
```

### CLI + YAML

```python
start: retrieve
nodes:
  - id: retrieve
    type: strategy.retrieve
    params: { name: chroma_query, path: .ff_chroma, collection: docs, k: 8 }
  - id: rerank
    type: strategy.rerank
    params: { name: bm25_preselect, top_k: 8 }
  - id: prompt
    type: prompt.rag
  - id: answer
    type: llm.chat
    params: { provider: echo, model: gpt-4o-mini }
edges:
  - { source: retrieve, target: rerank }
  - { source: rerank,   target: prompt }
  - { source: prompt,   target: answer }
```

Run:
```bash
flowfoundry run rag_local.yaml --state '{"query":"Hello!"}'
```

## Functional API Reference

Available in `flowfoundry.functional`:

---

### Chunking

| Function          | Purpose              | Extra deps |
|-------------------|----------------------|------------|
| `chunk_fixed`     | Fixed-size splitter  | –          |
| `chunk_recursive` | Recursive splitter   | `langchain-text-splitters` |
| `chunk_hybrid`    | Hybrid splitter      | –          |

```python
chunk_fixed(text, *, size=800, overlap=80, doc_id="doc") -> list[Chunk]
chunk_recursive(text, *, size=800, overlap=80, doc_id="doc") -> list[Chunk]
chunk_hybrid(text, **kwargs) -> list[Chunk]
```

---

### Indexing (Chroma)

| Function              | Purpose              | Extra deps |
|-----------------------|----------------------|------------|
| `index_chroma_upsert` | Upsert chunks into Chroma  |`chromadb` |
| `index_chroma_query`  | Query Chroma   | `chromadb` |

```python
index_chroma_upsert(chunks, *, path=".ff_chroma", collection="docs") -> str
index_chroma_query(query, *, k=5, path, collection) -> list[Hit]
```
---

### Indexing (Qdrant)

| Function              | Purpose              | Extra deps |
|-----------------------|----------------------|------------|
| `index_qdrant_upsert` | Upsert chunks into Qdrant  | `qdrant-client` |
| `index_qdrant_query`  | Query Qdrant   | `qdrant-client` |

```python
index_qdrant_upsert(chunks, *, url, collection, dim=None) -> str
index_qdrant_query(query, *, url, collection, k=5, vector=None) -> list[Hit]
```
---

### Reranking

| Function          | Purpose              | Extra deps |
|-------------------|----------------------|------------|
| `rerank_identity`     | No-op reranker  | –          |
| `preselect_bm25` | BM25 preselect   | `rank-bm25` |
| `rerank_cross_encoder`    | Cross-encoder reranker      |`sentence-transformers` |

```python
rerank_identity(query, hits) -> list[Hit]
preselect_bm25(query, hits, top_k=20) -> list[Hit]
rerank_cross_encoder(query, hits, *, model, top_k=None) -> list[Hit]
```