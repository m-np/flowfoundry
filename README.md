# FlowFoundry

> **FlowFoundry** is a cloud-agnostic **agentic workflow framework** built on LangGraph and LangChain.  
> It helps you design, test, and run agentic workflows locally or in the cloud, with pluggable connectors for storage, LLMs, rerankers, and external tools.

## Features
- 🔌 Cloud-agnostic core
- 🧠 Multi-LLM per node
- 🧪 Testable with in-memory components
- 🛠️ Extensible for RAG, tool use, DB retrieval, form filing, image interpretation

## Install
```bash
pip install flowfoundry           # core
pip install "flowfoundry[rag]"    # + Chroma & sentence-transformers
pip install "flowfoundry[rerank]" # + CrossEncoder & BM25
```

## Run a local RAG 
```bash
flowfoundry run examples/ingestion.yaml
flowfoundry run examples/rag_local.yaml --state '{"query":"What does the doc say about X?"}'
```
### Extend with a strategy
```python
from flowfoundry.strategies import register_strategy

@register_strategy("chunking", "my_smart_chunker")
def my_smart_chunker(text: str, *, doc_id: str = "doc"):
    return [{"doc": doc_id, "text": text}]
```
