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
├─ examples/                  # ready-to-run Python demos
├─ src/flowfoundry/
│  ├─ functional/             # core strategy functions (chunk, index, rerank, compose)
│  ├─ model/                  # LLM provider wrappers (openai, ollama, hf, langchain)
│  ├─ utils/                  # registry, errors, helpers
│  └─ cli.py                  # Typer CLI (auto-discovers functional strategies)
├─ tests/                     # pytest functional tests
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
from flowfoundry.functional import (
    chunk_recursive,
    index_chroma_upsert,
    index_chroma_query,
)

chunks = chunk_recursive("FlowFoundry example text", chunk_size=120, chunk_overlap=20, doc_id="demo")
index_chroma_upsert(chunks, path=".ff_chroma", collection="docs")
hits = index_chroma_query("What is FlowFoundry?", path=".ff_chroma", collection="docs", k=5)
```

### CLI

Every registered function is available automatically:
```bash
# list all available strategies
flowfoundry list

# run a strategy by family/name
flowfoundry call chunking fixed --kwargs '{"data":"hello world","chunk_size":5}'
```
Or use subcommands (auto-generated per family):
```bash
flowfoundry chunking fixed --kwargs '{"data":"hello world","chunk_size":5}'
flowfoundry indexing chroma_query --kwargs '{"q":"budget","path":".ff_chroma","collection":"docs"}'
```

Ready-to-run Python scripts are in examples/python/:

01_load_chunk_index.py – load PDFs, chunk, index into Chroma

02_query_rerank.py – query and rerank hits

03_compose_openai.py – retrieve + answer with OpenAI

04_compose_ollama.py – same but using local Ollama

06_pipeline_end_to_end.py – full pipeline in one script


Run:
```bash
python examples/python/01_load_chunk_index.py
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
