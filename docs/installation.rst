Installation
============

From PyPI (all extras)
----------------------

.. code-block:: bash

   python -m venv .venv && source .venv/bin/activate
   pip install "flowfoundry[rag,search,rerank,qdrant,openai,llm-openai]"

From source (editable)
----------------------

.. code-block:: bash

   python -m venv .venv && source .venv/bin/activate
   pip install -r docs/requirements.txt
   pip install -e ".[rag,search,rerank,qdrant,openai,llm-openai,dev]"

Extras
------

- ``rag``: ``chromadb``, ``sentence-transformers``
- ``search``: ``duckduckgo-search``, ``tavily-python``
- ``rerank``: ``sentence-transformers``, ``rank-bm25``
- ``qdrant``: ``qdrant-client``
- ``openai``: ``openai`` (raw SDK route)
- ``llm-openai``: ``langchain-openai`` (LangChain integration)
- ``dev``: tests & lint tools

All examples run offline (echo LLM). Missing optional deps are handled as no-ops.
