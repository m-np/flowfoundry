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
chunks = chunk_recursive(text, chunk_size=120, chunk_overlap=20, doc_id="demo")

# Index & query (requires chromadb extra)
index_chroma_upsert(chunks, path=".ff_chroma", collection="docs")
hits = index_chroma_query("What is FlowFoundry?", path=".ff_chroma", collection="docs", k=8)

# Optional rerank (requires rank-bm25)
hits = preselect_bm25("What is FlowFoundry?", hits, top_k=5)

print(hits[0]["text"])
```

### CLI

All registered strategies are available via the flowfoundry CLI.

Run:
```bash
# list families and functions
flowfoundry list

# call a strategy directly
flowfoundry chunking fixed --kwargs '{"data":"hello world","chunk_size":5}'

# equivalent generic call
flowfoundry call chunking fixed --kwargs '{"data":"hello world","chunk_size":5}'
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
chunk_fixed(text, *, chunk_size=800, chunk_overlap=80, doc_id="doc") -> list[Chunk]
chunk_recursive(text, *, chunk_size=800, chunk_overlap=80, doc_id="doc") -> list[Chunk]
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
index_chroma_query(query, *, path, collection, k=5) -> list[Hit]
```
---

### Reranking

| Function          | Purpose              | Extra deps |
|-------------------|----------------------|------------|
| `rerank_identity`     | No-op reranker  | –          |
| `preselect_bm25` | BM25 preselect   | `rank-bm25` |
| `rerank_cross_encoder`    | Cross-encoder reranker      |`sentence-transformers` |

```python
rerank_identity(query, hits, top_k=None) -> list[Hit]
preselect_bm25(query, hits, top_k=20) -> list[Hit]
rerank_cross_encoder(query, hits, *, model, top_k=None) -> list[Hit]
```

### Composition (LLM Answering)

| Function          | Purpose              | Providers supported | Extra deps |
|-------------------|----------------------|------------|----------------------|
| `compose_llm`     | Generate an answer from hits via an LLM  | openai, ollama, huggingface, langchain | provider-specific |

```python
compose_llm(
    question: str,
    hits: list[Hit],
    *,
    provider: str,        # "openai", "ollama", "huggingface", "langchain"
    model: str,           # e.g. "gpt-4o-mini", "llama3:8b", "distilgpt2"
    max_context_chars=6000,
    max_tokens=512,
    reuse_provider=True,
    **provider_kwargs     # api_key, host, backend, device, etc.
) -> str
```

## Example Code:
```python
from flowfoundry import index_chroma_query, preselect_bm25, compose_llm

question = "What is people's budget?"
hits = index_chroma_query(question, path=".ff_chroma", collection="docs", k=8)
hits = preselect_bm25(question, hits, top_k=5)

# OpenAI provider
answer = compose_llm(
    question, hits,
    provider="openai",
    model="gpt-4o-mini",
    max_tokens=400,
)
print(answer)

# Ollama provider
answer = compose_llm(
    question, hits,
    provider="ollama",
    model="llama3:8b",
    host="http://localhost:11434",
    max_tokens=400,
)
print(answer)

# HuggingFace local transformers
answer = compose_llm(
    question, hits,
    provider="huggingface",
    model="distilgpt2",
    max_tokens=200,
)
print(answer)
```

Example (CLI)

Save retrieval hits into JSON first, then pass them to compose_llm:

Step 1: query (Chroma)
```bash
flowfoundry indexing chroma_query \
  --kwargs '{"query":"What is people'\''s budget?","path":".ff_chroma","collection":"docs","k":8}' > hits.json
```

Step 2: rerank (BM25)
```bash
 flowfoundry rerank bm25_preselect \
  --kwargs "{\"query\":\"What is people's budget?\",\"hits\":$(cat hits.json),\"top_k\":5}" > hits_top5.json
```

Step 3: compose answer with OpenAI
``` bash
export OPENAI_API_KEY=...
flowfoundry compose llm \
  --kwargs "{\"question\":\"What is people's budget?\",\"hits\":$(cat hits_top5.json),\"provider\":\"openai\",\"model\":\"gpt-4o-mini\",\"max_tokens\":400}"
```

## YAML based run

Planned Schema:
```yaml
version: 1
vars:        # optional globals you can reference later
  key: value
steps:       # ordered list of steps
  - id: step_name
    use: family.function_name      # e.g., chunking.chunk_recursive
    with:                          # kwargs passed to that function
      param1: foo
      param2: ${{ vars.key }}      # reference vars or prior steps
outputs:     # optional; what to print at the end
  result: ${{ step_name }}
```

Example 1 — Minimal RAG (inline text)
```yaml
version: 1

vars:
  data_path: docs/samples/                   
  store_path: .ff_chroma2
  collection: docs
  question: "Summarize the pdfs"

steps:
  # 1) Load PDFs (your existing strategy)
  - id: pages
    use: ingestion.pdf_loader
    with:
      path: ${{ vars.data_path }}

  # 2) Chunk every page, preserving source/page metadata
  - id: chunks
    use: chunking.recursive
    with:
      data: ${{ pages }}
      chunk_size: 800
      chunk_overlap: 120

  # 3) Upsert chunks into Chroma
  - id: upsert
    use: indexing.chroma_upsert
    with:
      chunks: ${{ chunks }}
      path: ${{ vars.store_path }}
      collection: ${{ vars.collection }}

  # 4) Retrieve relevant chunks
  - id: retrieve
    use: indexing.chroma_query
    with:
      query: ${{ vars.question }}
      path: ${{ vars.store_path }}
      collection: ${{ vars.collection }}
      k: 12

  # 5) (Optional) BM25 preselect
  - id: preselect
    use: rerank.bm25_preselect
    with:
      query: ${{ vars.question }}
      hits: ${{ retrieve }}
      top_k: 6

  # 6) Compose final answer (pick your provider)
  - id: answer
    use: compose.llm
    with:
      question: ${{ vars.question }}
      hits: ${{ preselect }}
      provider: openai               # or "ollama" / "huggingface"
      model: gpt-4o-mini
      max_tokens: 400

outputs:
  final_answer: ${{ answer }}
```

Run:
```bash
pip install "flowfoundry[rag,rerank,openai,llm-openai]"
export OPENAI_API_KEY=...
flowfoundry run rag_samples.yaml
```