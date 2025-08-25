Ingestion
=========

Where to put documents
----------------------

The ``io.pdf_load`` node resolves ``params.path`` in this order:

1. ``pkg:<file>`` → packaged asset under ``flowfoundry/assets/<file>``
2. Absolute path → e.g. ``/data/refund.pdf``
3. Current working directory
4. Repo root (directory with ``pyproject.toml``)
5. ``$FLOWFOUNDRY_DATA_DIR`` (if set)

If the file is not found, the node prints every location it tried and uses a built-in sample text so the workflow still runs.

Recommended layouts
-------------------

Repo-local::

  your-project/
  ├─ pyproject.toml
  ├─ docs/               # put PDFs here
  │  └─ policies/refund.pdf
  └─ .ff_chroma/         # vector index (gitignore)

Shared data dir::

  export FLOWFOUNDRY_DATA_DIR="$HOME/data/flowfoundry"
  # place files under $FLOWFOUNDRY_DATA_DIR/docs/...

Ingest via CLI (YAML)
---------------------

.. code-block:: bash

   flowfoundry run examples/ingestion.yaml

Ingest via programmatic nodes
-----------------------------

.. code-block:: python

   from flowfoundry.config import WorkflowSpec, NodeSpec, EdgeSpec
   from flowfoundry.graphs.builder import compile_workflow

   spec = WorkflowSpec(
     start="load",
     nodes=[
       NodeSpec(id="load",   type="io.pdf_load",        params={"path": "docs/refund.pdf"}),
       NodeSpec(id="chunk",  type="strategy.chunking",  params={"name": "recursive", "size": 900, "overlap": 120}),
       NodeSpec(id="upsert", type="strategy.indexing",  params={"name": "chroma_upsert", "path": ".ff_chroma", "collection": "docs"}),
     ],
     edges=[EdgeSpec(source="load", target="chunk"), EdgeSpec(source="chunk", target="upsert")],
   )
   compile_workflow(spec).invoke({})
