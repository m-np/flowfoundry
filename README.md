# FlowFoundry

> **FlowFoundry** is a cloud-agnostic **agentic workflow framework** built on LangGraph and LangChain.  
> It helps you design, test, and run agentic workflows locally or in the cloud, with pluggable connectors for storage, LLMs, rerankers, and external tools.

## Features
- 🔌 Cloud-agnostic core
- 🧠 Multi-LLM per node
- 🧪 Testable with in-memory components
- 🛠️ Extensible for RAG, tool use, DB retrieval, form filing, image interpretation

## 📦 Install

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[rag,search,rerank,qdrant,openai,llm-openai,dev]"
```
Examples run offline with echo LLM. Optional extras no-op gracefully.

## Repository layout
```bash
flowfoundry/
├─ examples/                  # ready-to-run YAML + Python demos
├─ src/flowfoundry/
│  ├─ functional/             # core strategy functions (single source of truth)
│  ├─ blocks/                 # wrappers for composition
│  ├─ nodes/                  # registered node types (io, llm, prompt, strategy.*)
│  ├─ graphs/                 # LangGraph compiler & helpers
│  ├─ cli.py                  # Typer CLI (run/list/serve)
│  ├─ api.py                  # FastAPI local service
│  └─ assets/                 # bundled demo data
├─ docs/                      # Sphinx docs
├─ tests/                     # pytest suite
├─ pyproject.toml
└─ Makefile
```

## Concepts

- Strategy: pure function (e.g. chunk_recursive)

- Functional API: call strategies directly

- Blocks: wrappers with config (Recursive, ChromaUpsert, etc.)

- Node: registered stateful step in LangGraph

- Workflow: nodes + edges compiled into a runnable graph

## Examples

### Functional API

```python
from flowfoundry.functional import chunk_recursive, index_chroma_upsert, index_chroma_query

chunks = chunk_recursive("FlowFoundry example text", size=120, overlap=20, doc_id="demo")
index_chroma_upsert(chunks, path=".ff_chroma", collection="docs")
hits = index_chroma_query("What is FlowFoundry?", path=".ff_chroma", collection="docs", k=5)
```

### Blocks
```python
from flowfoundry.blocks import Recursive, ChromaUpsert, ChromaQuery

chunks = Recursive(size=120, overlap=20)(text="Some text", doc_id="demo")
ChromaUpsert(path=".ff_chroma", collection="docs")(chunks=chunks)
hits = ChromaQuery(path=".ff_chroma", collection="docs", k=5)(query="demo?")
```

### YAML + CLI
```yaml
start: retrieve
nodes:
  - id: retrieve
    type: strategy.retrieve
    params: { name: chroma_query, path: .ff_chroma, collection: docs, k: 8 }
  - id: answer
    type: llm.chat
    params: { provider: echo }
edges:
  - { source: retrieve, target: answer }

```
Run:
```bash
flowfoundry run examples/rag_local.yaml --state '{"query":"Hello!"}'
```

## Development
```bash
make dev      # editable install + extras
make test     # run pytest
make docs     # build Sphinx docs
```
Pre-commit hooks:
```bash
pre-commit install
pre-commit run --all-files
```

## Contributing

- Fork the repo

- Create a branch: git checkout -b feat/my-feature

- Commit + push

- Open a PR


## Docs

Build locally:
```bash
cd docs && make html
open _build/html/index.html
```
