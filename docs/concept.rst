Concepts
========

- **Strategy**: the *what* (pure function: chunk, index, retrieve, rerank).
- **Functional API**: call a strategy directly (no orchestration).
- **Blocks**: thin object wrappers around functional strategies.
- **Node**: a registered, stateful workflow step (LangGraph node).
- **Workflow**: nodes + edges + a start node, compiled and executed.

Architecture
------------

.. mermaid::

   flowchart LR
     subgraph Functional (single source of truth)
       CF[chunk_fixed]
       CR[chunk_recursive]
       CHY[chunk_hybrid]
       CU[index_chroma_upsert]
       CQ[index_chroma_query]
       QU[index_qdrant_upsert]
       QQ[index_qdrant_query]
       RId[rerank_identity]
       RBM[preselect_bm25]
       RCE[rerank_cross_encoder]
     end

     subgraph Blocks (thin wrappers)
       BF[Fixed]
       BR[Recursive]
       BH[Hybrid]
       BCU[ChromaUpsert]
       BCQ[ChromaQuery]
       BQU[QdrantUpsert]
       BQQ[QdrantQuery]
       BID[Identity]
       BBM[BM25]
       BCE[CrossEncoder]
     end

     subgraph Nodes (workflow steps)
       NPDF[io.pdf_load]
       NCHUNK[strategy.chunking]
       NINDEX[strategy.indexing]
       NRETR[strategy.retrieve]
       NRR[strategy.rerank]
       NPROMPT[prompt.rag]
       NLLM[llm.chat]
     end

     CF --> BF
     CR --> BR
     CHY --> BH
     CU --> BCU
     CQ --> BCQ
     QU --> BQU
     QQ --> BQQ
     RId --> BID
     RBM --> BBM
     RCE --> BCE

     BF --> NCHUNK
     BR --> NCHUNK
     BH --> NCHUNK
     BCU --> NINDEX
     BCQ --> NRETR
     BQU --> NINDEX
     BQQ --> NRETR
     BID --> NRR
     BBM --> NRR
     BCE --> NRR

     NPDF --> NCHUNK --> NINDEX
     NRETR --> NRR --> NPROMPT --> NLLM

Repository Layout
-----------------

.. code-block:: text

   src/flowfoundry/
   ├─ functional/              # ✅ Single source of strategy logic
   ├─ blocks/                  # Thin wrappers over functional
   ├─ nodes/                   # LangGraph nodes that call functional
   ├─ graphs/builder.py        # WorkflowSpec → LangGraph compiler
   ├─ registry.py              # node registry + entrypoint loader
   ├─ strategies/registry.py   # strategy registry + decorator
   └─ assets/                  # optional packaged assets (e.g., sample.pdf)
