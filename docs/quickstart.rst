Quickstart
==========

Functional API (fastest)
------------------------

.. code-block:: python

   from flowfoundry.functional import (
       chunk_recursive, index_chroma_upsert, index_chroma_query, preselect_bm25
   )

   text = "FlowFoundry lets you mix strategies to build RAG."
   chunks = chunk_recursive(text, size=120, overlap=20, doc_id="demo")
   index  = index_chroma_upsert(chunks, path=".ff_chroma", collection="docs")
   hits   = index_chroma_query("What is FlowFoundry?", path=".ff_chroma", collection="docs", k=8)
   hits   = preselect_bm25("What is FlowFoundry?", hits, top_k=5)
   print(hits[0]["text"])

YAML + CLI
----------

.. code-block:: yaml

   # examples/ingestion.yaml
   start: load
   nodes:
     - id: load
       type: io.pdf_load
       params: { path: pkg:sample.pdf }
     - id: chunk
       type: strategy.chunking
       params: { name: recursive, size: 900, overlap: 120 }
     - id: upsert
       type: strategy.indexing
       params: { name: chroma_upsert, path: .ff_chroma, collection: docs }
   edges:
     - { source: load, target: chunk }
     - { source: chunk, target: upsert }

.. code-block:: bash

   flowfoundry run examples/ingestion.yaml

Programmatic Nodes + LangGraph
------------------------------

.. code-block:: python

   from flowfoundry.config import WorkflowSpec, NodeSpec, EdgeSpec
   from flowfoundry.graphs.builder import compile_workflow

   spec = WorkflowSpec(
       start="retrieve",
       nodes=[
           NodeSpec(id="retrieve", type="strategy.retrieve",
                    params={"name":"chroma_query","path":".ff_chroma","collection":"docs","k":8}),
           NodeSpec(id="rerank",   type="strategy.rerank", params={"name":"bm25_preselect","top_k":8}),
           NodeSpec(id="prompt",   type="prompt.rag",      params={}),
           NodeSpec(id="answer",   type="llm.chat",        params={"provider":"echo","model":"gpt-4o-mini"}),
       ],
       edges=[
           EdgeSpec(source="retrieve", target="rerank"),
           EdgeSpec(source="rerank",   target="prompt"),
           EdgeSpec(source="prompt",   target="answer"),
       ],
   )

   out = compile_workflow(spec).invoke({"query":"Summarize the refund policy."})
   print(out["answer"])
