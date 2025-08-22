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
pip install flowfoundry
```

## Quickstart
```python
from flowfoundry import ping
from flowfoundry.hello import hello

print(ping())           # "flowfoundry: ok"
print(hello("dev"))     # "hello, dev!"
```
